"""Service for managing conversation history in the AI chat system."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select, desc, asc
from src.models.conversation import ConversationMessage, ConversationHistory


class ConversationService:
    """Service for managing conversation history."""

    def __init__(self):
        pass

    def get_or_create_conversation(self, session: Session, user_id: str) -> str:
        """
        Get an existing active conversation for the user or create a new one.

        Args:
            session: Database session
            user_id: ID of the user

        Returns:
            Conversation ID
        """
        # Try to find an active conversation for this user
        statement = select(ConversationHistory).where(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_active == True
        ).order_by(desc(ConversationHistory.updated_at)).limit(1)

        existing_conversation = session.exec(statement).first()

        if existing_conversation:
            assert existing_conversation.id is not None, "Existing conversation should have an ID"
            return existing_conversation.id

        # Create a new conversation
        conversation_id = str(uuid.uuid4())
        new_conversation = ConversationHistory(
            id=conversation_id,
            user_id=user_id,
            title="New Conversation",
            is_active=True
        )

        session.add(new_conversation)
        session.commit()
        session.refresh(new_conversation)

        assert new_conversation.id is not None, "New conversation should have an ID after being saved"
        return new_conversation.id

    def add_message(self, session: Session, user_id: str, conversation_id: str, role: str, content: str) -> ConversationMessage:
        """
        Add a message to the conversation history.

        Args:
            session: Database session
            user_id: ID of the user
            conversation_id: ID of the conversation
            role: Role of the message sender ('user' or 'assistant')
            content: Content of the message

        Returns:
            Created ConversationMessage object
        """
        message = ConversationMessage(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        return message

    def get_recent_messages(self, session: Session, conversation_id: str, limit: int = 10) -> List[ConversationMessage]:
        """
        Get recent messages from a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return

        Returns:
            List of ConversationMessage objects
        """
        statement = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(desc(ConversationMessage.timestamp)).limit(limit)

        messages = list(session.exec(statement).all())
        return list(reversed(messages))  # Return in chronological order

    def get_full_conversation(self, session: Session, conversation_id: str) -> List[ConversationMessage]:
        """
        Get all messages from a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation

        Returns:
            List of ConversationMessage objects
        """
        statement = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(asc(ConversationMessage.timestamp))

        messages = list(session.exec(statement).all())
        return messages

    def update_conversation_title(self, session: Session, conversation_id: str, title: str):
        """
        Update the title of a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            title: New title for the conversation
        """
        statement = select(ConversationHistory).where(ConversationHistory.id == conversation_id)
        conversation = session.exec(statement).first()

        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)
            session.commit()

    def get_user_conversations(self, session: Session, user_id: str) -> List[ConversationHistory]:
        """
        Get all conversations for a user.

        Args:
            session: Database session
            user_id: ID of the user

        Returns:
            List of ConversationHistory objects
        """
        statement = select(ConversationHistory).where(
            ConversationHistory.user_id == user_id
        ).order_by(desc(ConversationHistory.updated_at))

        conversations = list(session.exec(statement).all())
        return conversations

    def end_conversation(self, session: Session, conversation_id: str):
        """
        Mark a conversation as inactive.

        Args:
            session: Database session
            conversation_id: ID of the conversation to end
        """
        statement = select(ConversationHistory).where(ConversationHistory.id == conversation_id)
        conversation = session.exec(statement).first()

        if conversation:
            conversation.is_active = False
            session.add(conversation)
            session.commit()


# Global instance
conversation_service = ConversationService()