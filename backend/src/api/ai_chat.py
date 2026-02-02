"""API endpoints for AI chatbot functionality."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ..api.deps import get_current_user
from ..ai_chatbot.processors.input_processor import input_processor
from ..ai_chatbot.utils.logging import agent_logger, security_logger
from ..database.session import get_session
from ..ai_chatbot.services.conversation_service import conversation_service
from ..models.conversation import ConversationMessage
from sqlmodel import Session

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    success: bool
    user_id: Optional[str] = None


@router.post("/api/ai/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat endpoint that processes natural language requests and maps to MCP tools.

    Args:
        request: Chat request containing the user message
        current_user: Authenticated user from JWT token

    Returns:
        ChatResponse with the AI-generated response
    """
    # Extract user ID and raw token from current user context (same as tasks endpoint but with token for tools)
    user_id = current_user.get("sub")
    token = current_user.get("raw_token", "")
    username = current_user.get("username", current_user.get("email", "unknown"))

    security_logger.log_auth_attempt(user_id, True)

    try:
        # Get or create a conversation for this user
        with next(get_session()) as session:
            conversation_id = conversation_service.get_or_create_conversation(session, user_id)

            # Add the user's message to the conversation history
            user_message = conversation_service.add_message(
                session=session,
                user_id=user_id,
                conversation_id=conversation_id,
                role="user",
                content=request.message
            )

            # Process the natural language input
            response_text = await input_processor.process_input(
                text=request.message,
                token=token,  # Use the raw token for tools that need to make authenticated API calls
                user_id=user_id
            )

            # Add the assistant's response to the conversation history
            assistant_message = conversation_service.add_message(
                session=session,
                user_id=user_id,
                conversation_id=conversation_id,
                role="assistant",
                content=response_text
            )

            # Update conversation title if it's the first message
            conversation_messages = conversation_service.get_full_conversation(session, conversation_id)
            if len(conversation_messages) == 2:  # Just user and assistant first messages
                # Use the first few words of the user's message as the title
                title = request.message.strip()[:50] + "..." if len(request.message.strip()) > 50 else request.message.strip()
                conversation_service.update_conversation_title(session, conversation_id, title)

        agent_logger.info(
            f"Processed chat request for user {user_id}",
            context={"request_length": len(request.message)},
            user_id=user_id
        )

        return ChatResponse(
            response=response_text,
            success=True,
            user_id=user_id
        )

    except Exception as e:
        agent_logger.error(
            f"Error processing chat request: {str(e)}",
            context={"request_length": len(request.message)},
            user_id=user_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your request"
        )


@router.get("/api/ai/chat/tools")
async def get_available_tools(current_user: dict = Depends(get_current_user)):
    """
    Get list of available tools for the AI agent.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        Dictionary of available tools
    """
    # Extract user ID and raw token from current user context (same as tasks endpoint but with token for tools)
    user_id = current_user.get("sub")
    token = current_user.get("raw_token", "")
    username = current_user.get("username", current_user.get("email", "unknown"))

    security_logger.log_auth_attempt(user_id, True)


    # Import here to avoid circular imports
    from ..ai_chatbot.agents.cohere_agent import chatbot_agent
    tools = chatbot_agent.get_available_tools()

    agent_logger.info(
        f"Retrieved tools list for user {user_id}",
        context={"tool_count": len(tools)},
        user_id=user_id
    )

    return tools