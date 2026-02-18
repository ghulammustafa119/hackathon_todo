"""Models for tags and task-tag many-to-many relationship."""

from typing import Optional
from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """User-scoped tag for organizing tasks."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, index=True)
    user_id: str = Field(index=True)


class TaskTag(SQLModel, table=True):
    """Junction table for Task-Tag many-to-many relationship."""

    task_id: str = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
