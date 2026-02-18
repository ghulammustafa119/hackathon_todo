"""Models for conversation history in the AI chat system."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column
import sqlalchemy as sa


class ConversationMessage(SQLModel, table=True):
    """Model representing a message in a conversation."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    role: str = Field(max_length=20)  # user, assistant, system
    content: str = Field(sa_column_kwargs={"nullable": False})
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    conversation_id: str = Field(index=True)
    # Phase V extensions
    task_references: Optional[str] = Field(default=None, sa_column=Column(sa.Text))  # JSON array of task IDs
    token_count: Optional[int] = Field(default=None)
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(sa.Text))  # JSON tool call summaries


class ConversationHistory(SQLModel, table=True):
    """Model representing a conversation thread (legacy, kept for compatibility)."""

    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    # Phase V extensions
    message_count: int = Field(default=0)
    timeout_minutes: int = Field(default=30)
