from sqlmodel import Session, select
from typing import List, Optional
from src.models.task import Task, TaskCreate, TaskUpdate
from datetime import datetime
import pytz

class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task_data: TaskCreate, user_id: str) -> Task:
        """Create a new task for the specified user."""
        try:
            task = Task(
                title=task_data.title,
                description=task_data.description,
                user_id=user_id,
                completed=task_data.completed if hasattr(task_data, 'completed') else False
            )
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
            return task
        except Exception as e:
            self.session.rollback()
            raise e

    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Get all tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

    def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get a specific task by ID for a specific user."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.session.exec(statement).first()

    def update_task(self, task_id: str, task_data: TaskUpdate, user_id: str) -> Optional[Task]:
        """Update a specific task for a specific user."""
        try:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Update only the fields that are provided in task_data
            if task_data.title is not None:
                task.title = task_data.title
            if task_data.description is not None:
                task.description = task_data.description
            if task_data.completed is not None:
                task.completed = task_data.completed
                if task.completed and task.completed_at is None:
                    pk_tz = pytz.timezone('Asia/Karachi')
                    pk_time = datetime.now(pk_tz)
                    task.completed_at = pk_time
                elif not task.completed:
                    task.completed_at = None

            pk_tz = pytz.timezone('Asia/Karachi')
            pk_time = datetime.now(pk_tz)
            task.updated_at = pk_time
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
            return task
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a specific task for a specific user."""
        try:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return False

            self.session.delete(task)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e

    def toggle_task_completion(self, task_id: str, user_id: str) -> Optional[Task]:
        """Toggle the completion status of a specific task for a specific user."""
        try:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return None

            task.completed = not task.completed
            if task.completed:
                pk_tz = pytz.timezone('Asia/Karachi')
                pk_time = datetime.now(pk_tz)
                task.completed_at = pk_time
            else:
                task.completed_at = None

            pk_tz = pytz.timezone('Asia/Karachi')
            pk_time = datetime.now(pk_tz)
            task.updated_at = pk_time
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
            return task
        except Exception as e:
            self.session.rollback()
            raise e

    def get_completed_tasks(self, user_id: str) -> List[Task]:
        """Get all completed tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id, Task.completed == True)
        return self.session.exec(statement).all()

    def get_pending_tasks(self, user_id: str) -> List[Task]:
        """Get all pending (not completed) tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id, Task.completed == False)
        return self.session.exec(statement).all()