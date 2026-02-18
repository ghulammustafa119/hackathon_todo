"""Models for task events and outbox pattern."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column
import sqlalchemy as sa
import uuid


class TaskEvent(SQLModel, table=True):
    """Represents a published task event (CloudEvents v1.0 compatible)."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    event_type: str = Field(index=True)  # task.created, task.updated, task.deleted, task.completed
    task_id: str = Field(index=True)
    user_id: str = Field(index=True)
    payload: str = Field(sa_column=Column(sa.Text))  # JSON string of full task state
    previous_state: Optional[str] = Field(default=None, sa_column=Column(sa.Text))  # JSON for updates
    schema_version: int = Field(default=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutboxEvent(SQLModel, table=True):
    """Transactional outbox for reliable event publishing."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    event_type: str = Field()
    topic: str = Field(default="tasks")
    payload: str = Field(sa_column=Column(sa.Text))  # JSON string
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = Field(default=None)
    retry_count: int = Field(default=0)
