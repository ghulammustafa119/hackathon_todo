from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid
import pytz

class TaskBase(SQLModel):
    title: str = Field(min_length=1)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

class TaskCreateBase(SQLModel):
    title: str = Field(min_length=1)
    description: Optional[str] = Field(default=None)

class Task(TaskBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)  # User ID from Better Auth JWT token

    @staticmethod
    def _get_pakistani_time():
        pk_tz = pytz.timezone('Asia/Karachi')
        pk_time = datetime.now(pk_tz)
        return pk_time

    created_at: datetime = Field(default_factory=_get_pakistani_time)
    updated_at: datetime = Field(default_factory=_get_pakistani_time)
    completed_at: Optional[datetime] = Field(default=None)

class TaskRead(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class TaskCreate(TaskCreateBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None