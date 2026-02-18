"""Model for reminder schedules."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class ReminderSchedule(SQLModel, table=True):
    """Tracks scheduled reminders for tasks with due dates."""

    __tablename__ = "reminder_schedule"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    task_id: str = Field(index=True, unique=True)  # One reminder per task
    user_id: str = Field(index=True)
    remind_at: datetime = Field(index=True)  # When to fire
    status: str = Field(default="pending")  # pending, sent, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
