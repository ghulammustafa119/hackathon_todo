"""Model for audit trail entries."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column
import sqlalchemy as sa
import uuid


class AuditEntry(SQLModel, table=True):
    """Immutable audit log entry for task operations."""

    __tablename__ = "audit_entries"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(index=True)
    operation_type: str = Field()  # CREATE, UPDATE, DELETE, COMPLETE
    task_id: str = Field(index=True)
    previous_state: Optional[str] = Field(default=None, sa_column=Column(sa.Text))
    new_state: str = Field(sa_column=Column(sa.Text))
    event_id: str = Field(unique=True)  # Idempotency key
    schema_version: int = Field(default=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
