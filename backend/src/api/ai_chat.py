"""API endpoints for AI chatbot functionality."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from ..ai_chatbot.processors.input_processor import input_processor
from ..ai_chatbot.utils.jwt_handler import validate_and_extract_user_context
from ..ai_chatbot.utils.logging import agent_logger, security_logger

router = APIRouter()
security = HTTPBearer()


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
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Chat endpoint that processes natural language requests and maps to MCP tools.

    Args:
        request: Chat request containing the user message
        credentials: JWT token for authentication

    Returns:
        ChatResponse with the AI-generated response
    """
    token = credentials.credentials

    # Validate and extract user context from JWT
    user_context = validate_and_extract_user_context(token)
    if not user_context:
        security_logger.log_auth_attempt("unknown", False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    user_id = user_context.get("user_id")
    security_logger.log_auth_attempt(user_id, True)


    try:
        # Process the natural language input
        response_text = await input_processor.process_input(
            text=request.message,
            token=token,
            user_id=user_id
        )

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
async def get_available_tools(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get list of available tools for the AI agent.

    Args:
        credentials: JWT token for authentication

    Returns:
        Dictionary of available tools
    """
    token = credentials.credentials

    # Validate and extract user context from JWT
    user_context = validate_and_extract_user_context(token)
    if not user_context:
        security_logger.log_auth_attempt("unknown", False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    user_id = user_context.get("user_id")
    security_logger.log_auth_attempt(user_id, True)


    # Import here to avoid circular imports
    from ..ai_chatbot.agents.openai_agent import chatbot_agent
    tools = chatbot_agent.get_available_tools()

    agent_logger.info(
        f"Retrieved tools list for user {user_id}",
        context={"tool_count": len(tools)},
        user_id=user_id
    )

    return tools