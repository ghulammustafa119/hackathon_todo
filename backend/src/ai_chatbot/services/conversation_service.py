"""Service for managing conversation history in the AI chat system."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlmodel import Session, select, desc, asc
from src.models.conversation import ConversationMessage, ConversationHistory

SESSION_TIMEOUT_MINUTES = 30
SLIDING_WINDOW_SIZE = 20
TOKEN_BUDGET = 4000


class ConversationService:
    """Service for managing conversation history with session timeout and sliding window."""

    def __init__(self):
        pass

    def get_or_create_conversation(self, session: Session, user_id: str) -> str:
        """Get active conversation or create new one. Expires after SESSION_TIMEOUT_MINUTES."""
        statement = select(ConversationHistory).where(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_active == True
        ).order_by(desc(ConversationHistory.updated_at)).limit(1)

        existing = session.exec(statement).first()

        if existing:
            # Check session timeout
            elapsed = datetime.now(timezone.utc) - existing.updated_at.replace(tzinfo=timezone.utc)
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                # Expire old session
                existing.is_active = False
                session.add(existing)
                session.commit()
            else:
                assert existing.id is not None
                return existing.id

        # Create new conversation
        conversation_id = str(uuid.uuid4())
        new_conversation = ConversationHistory(
            id=conversation_id,
            user_id=user_id,
            title="New Conversation",
            is_active=True,
            timeout_minutes=SESSION_TIMEOUT_MINUTES,
        )
        session.add(new_conversation)
        session.commit()
        session.refresh(new_conversation)
        assert new_conversation.id is not None
        return new_conversation.id

    def add_message(
        self,
        session: Session,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        task_references: Optional[str] = None,
    ) -> ConversationMessage:
        """Add a message to the conversation history."""
        message = ConversationMessage(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            task_references=task_references,
            token_count=len(content.split()),  # Approximate token count
        )
        session.add(message)

        # Update conversation metadata
        conv = session.exec(
            select(ConversationHistory).where(ConversationHistory.id == conversation_id)
        ).first()
        if conv:
            conv.updated_at = datetime.now(timezone.utc)
            conv.message_count += 1
            session.add(conv)

        session.commit()
        session.refresh(message)
        return message

    def get_sliding_window_context(
        self, session: Session, conversation_id: str
    ) -> List[dict]:
        """Get last N messages within token budget for LLM context.

        Returns list of {role, content} dicts suitable for chat API.
        """
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(desc(ConversationMessage.timestamp))
            .limit(SLIDING_WINDOW_SIZE)
        )
        messages = list(session.exec(statement).all())
        messages.reverse()  # Chronological order

        # Trim to token budget
        context = []
        total_tokens = 0
        for msg in messages:
            tokens = msg.token_count or len(msg.content.split())
            if total_tokens + tokens > TOKEN_BUDGET:
                break
            context.append({"role": msg.role, "content": msg.content})
            total_tokens += tokens

        return context

    def get_recent_messages(
        self, session: Session, conversation_id: str, limit: int = 10
    ) -> List[ConversationMessage]:
        """Get recent messages from a conversation."""
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(desc(ConversationMessage.timestamp))
            .limit(limit)
        )
        messages = list(session.exec(statement).all())
        return list(reversed(messages))

    def get_full_conversation(
        self, session: Session, conversation_id: str
    ) -> List[ConversationMessage]:
        """Get all messages from a conversation."""
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(asc(ConversationMessage.timestamp))
        )
        return list(session.exec(statement).all())

    def update_conversation_title(
        self, session: Session, conversation_id: str, title: str
    ):
        """Update the title of a conversation."""
        statement = select(ConversationHistory).where(
            ConversationHistory.id == conversation_id
        )
        conversation = session.exec(statement).first()
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)
            session.commit()

    def get_user_conversations(
        self, session: Session, user_id: str
    ) -> List[ConversationHistory]:
        """Get all conversations for a user."""
        statement = (
            select(ConversationHistory)
            .where(ConversationHistory.user_id == user_id)
            .order_by(desc(ConversationHistory.updated_at))
        )
        return list(session.exec(statement).all())

    def end_conversation(self, session: Session, conversation_id: str):
        """Mark a conversation as inactive."""
        statement = select(ConversationHistory).where(
            ConversationHistory.id == conversation_id
        )
        conversation = session.exec(statement).first()
        if conversation:
            conversation.is_active = False
            session.add(conversation)
            session.commit()


# Global instance
conversation_service = ConversationService()
