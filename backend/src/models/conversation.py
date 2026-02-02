"""Models for conversation history in the AI chat system."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class ConversationMessage(SQLModel, table=True):
    """Model representing a message in a conversation."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Reference to the user who sent the message
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(sa_column_kwargs={"nullable": False})
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Add conversation_id to group related messages together
    conversation_id: str = Field(index=True)


class ConversationHistory(SQLModel, table=True):
    """Model representing a conversation thread."""

    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Reference to the user who started the conversation
    title: str = Field(max_length=255)  # Auto-generated title based on first message
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)  # Whether this conversation is currently active