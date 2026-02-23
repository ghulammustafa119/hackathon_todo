from sqlmodel import Session, select, col, text
from typing import List, Optional
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.tag import Tag, TaskTag
from src.models.event import TaskEvent, OutboxEvent
from src.models.reminder import ReminderSchedule
from datetime import datetime, timezone, timedelta
import json
import uuid
import logging
import pytz

logger = logging.getLogger("task-service")


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def _sync_reminder(self, task: Task):
        """Create or update a ReminderSchedule when a task has a due_date."""
        try:
            # Remove existing reminder for this task
            existing = self.session.exec(
                select(ReminderSchedule).where(ReminderSchedule.task_id == task.id)
            ).first()
            if existing:
                self.session.delete(existing)
                self.session.commit()

            if task.due_date and not task.completed:
                lead_minutes = task.reminder_lead_time or 60
                remind_at = task.due_date - timedelta(minutes=lead_minutes)
                # Only schedule if remind_at is in the future
                if remind_at > datetime.now():
                    reminder = ReminderSchedule(
                        task_id=task.id,
                        user_id=task.user_id,
                        remind_at=remind_at,
                        status="sent",  # immediately available for bell
                    )
                    self.session.add(reminder)
                    self.session.commit()
                    logger.info(f"Reminder scheduled for task {task.id} at {remind_at}")
        except Exception as e:
            logger.warning(f"Failed to sync reminder for task {task.id}: {e}")

    def _emit_event(self, event_type: str, task: Task, previous_state: Optional[dict] = None):
        """Persist task event to database and outbox for reliable delivery."""
        try:
            event_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            payload = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_rule": task.recurrence_rule,
                "user_id": task.user_id,
            }

            task_event = TaskEvent(
                event_id=event_id,
                event_type=event_type,
                task_id=task.id,
                user_id=task.user_id,
                payload=json.dumps(payload),
                previous_state=json.dumps(previous_state) if previous_state else None,
                schema_version=1,
                timestamp=now,
            )
            self.session.add(task_event)

            outbox_event = OutboxEvent(
                event_type=event_type,
                topic="tasks",
                payload=json.dumps({
                    "specversion": "1.0",
                    "type": f"com.todo.{event_type}",
                    "source": "/backend/task-service",
                    "id": event_id,
                    "time": now.isoformat(),
                    "data": payload,
                    "previous_state": previous_state,
                }),
            )
            self.session.add(outbox_event)
            self.session.commit()
            logger.info(f"Event {event_type} emitted for task {task.id}")
        except Exception as e:
            self.session.rollback()
            logger.warning(f"Failed to emit event {event_type}: {e}")

    def create_task(self, task_data: TaskCreate, user_id: str) -> Task:
        """Create a new task for the specified user."""
        try:
            task = Task(
                title=task_data.title,
                description=task_data.description,
                user_id=user_id,
                priority=task_data.priority or "medium",
                due_date=task_data.due_date,
                reminder_lead_time=task_data.reminder_lead_time or 60,
                recurrence_rule=task_data.recurrence_rule,
            )
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Handle tags
            if task_data.tags:
                self._set_task_tags(task.id, user_id, task_data.tags)

            # Schedule reminder if due_date is set
            self._sync_reminder(task)

            # Emit task.created event
            self._emit_event("task.created", task)

            return task
        except Exception as e:
            self.session.rollback()
            raise e

    def get_tasks_by_user(
        self,
        user_id: str,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Task]:
        """Get all tasks for a specific user with optional filtering and sorting."""
        statement = select(Task).where(Task.user_id == user_id)

        # Filter by priority
        if priority:
            statement = statement.where(Task.priority == priority)

        # Filter by status
        if status == "completed":
            statement = statement.where(Task.completed == True)
        elif status == "pending":
            statement = statement.where(Task.completed == False)

        # Filter by tag
        if tag:
            tag_obj = self.session.exec(
                select(Tag).where(Tag.user_id == user_id, Tag.name == tag)
            ).first()
            if tag_obj:
                task_ids = self.session.exec(
                    select(TaskTag.task_id).where(TaskTag.tag_id == tag_obj.id)
                ).all()
                statement = statement.where(col(Task.id).in_(task_ids))
            else:
                return []

        # Sort
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        tasks = self.session.exec(statement).all()

        # Full-text search (filter in Python — searches title, description, and tags)
        if search:
            search_lower = search.lower()
            # Pre-fetch tags for all tasks to check in search
            task_tags_map: dict = {}
            for t in tasks:
                task_tags_map[t.id] = self.get_task_tags(t.id)

            tasks = [
                t for t in tasks
                if search_lower in t.title.lower()
                or (t.description and search_lower in t.description.lower())
                or any(search_lower in tag.lower() for tag in task_tags_map.get(t.id, []))
            ]

        return tasks

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

            # Capture previous state for event
            previous_state = {
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_rule": task.recurrence_rule,
            }

            if task_data.title is not None:
                task.title = task_data.title
            if task_data.description is not None:
                task.description = task_data.description
            if task_data.completed is not None:
                task.completed = task_data.completed
                if task.completed and task.completed_at is None:
                    pk_tz = pytz.timezone('Asia/Karachi')
                    task.completed_at = datetime.now(pk_tz)
                elif not task.completed:
                    task.completed_at = None
            if task_data.priority is not None:
                task.priority = task_data.priority
            if task_data.due_date is not None:
                task.due_date = task_data.due_date
            if task_data.reminder_lead_time is not None:
                task.reminder_lead_time = task_data.reminder_lead_time
            if task_data.recurrence_rule is not None:
                task.recurrence_rule = task_data.recurrence_rule

            pk_tz = pytz.timezone('Asia/Karachi')
            task.updated_at = datetime.now(pk_tz)
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Handle tags
            if task_data.tags is not None:
                self._set_task_tags(task.id, user_id, task_data.tags)

            # Update reminder schedule
            self._sync_reminder(task)

            # Emit task.updated event
            self._emit_event("task.updated", task, previous_state)

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

            # Emit task.deleted event before deleting
            self._emit_event("task.deleted", task)

            # Remove reminder
            existing_reminder = self.session.exec(
                select(ReminderSchedule).where(ReminderSchedule.task_id == task_id)
            ).first()
            if existing_reminder:
                self.session.delete(existing_reminder)

            # Remove tag associations
            tag_links = self.session.exec(
                select(TaskTag).where(TaskTag.task_id == task_id)
            ).all()
            for link in tag_links:
                self.session.delete(link)

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
                task.completed_at = datetime.now(pk_tz)
            else:
                task.completed_at = None

            pk_tz = pytz.timezone('Asia/Karachi')
            task.updated_at = datetime.now(pk_tz)
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Sync reminder (removes if completed, schedules if uncompleted with due_date)
            self._sync_reminder(task)

            # Emit task.completed event
            self._emit_event("task.completed" if task.completed else "task.uncompleted", task)

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

    # --- Tag operations ---

    def _set_task_tags(self, task_id: str, user_id: str, tag_names: List[str]):
        """Set the tags for a task, creating new tags as needed."""
        # Remove existing tag links
        existing = self.session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        for link in existing:
            self.session.delete(link)

        # Add new tags
        for name in tag_names:
            name = name.strip()
            if not name:
                continue
            tag = self.session.exec(
                select(Tag).where(Tag.user_id == user_id, Tag.name == name)
            ).first()
            if not tag:
                tag = Tag(name=name, user_id=user_id)
                self.session.add(tag)
                self.session.commit()
                self.session.refresh(tag)
            self.session.add(TaskTag(task_id=task_id, tag_id=tag.id))

        self.session.commit()

    def get_task_tags(self, task_id: str) -> List[str]:
        """Get tag names for a task."""
        tag_links = self.session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        tag_ids = [link.tag_id for link in tag_links]
        if not tag_ids:
            return []
        tags = self.session.exec(
            select(Tag).where(col(Tag.id).in_(tag_ids))
        ).all()
        return [t.name for t in tags]

    def get_user_tags(self, user_id: str) -> List[Tag]:
        """Get all tags for a user."""
        return self.session.exec(
            select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
        ).all()

    def add_tags(self, task_id: str, user_id: str, tag_names: List[str]):
        """Add tags to a task without removing existing ones."""
        for name in tag_names:
            name = name.strip()
            if not name:
                continue
            tag = self.session.exec(
                select(Tag).where(Tag.user_id == user_id, Tag.name == name)
            ).first()
            if not tag:
                tag = Tag(name=name, user_id=user_id)
                self.session.add(tag)
                self.session.commit()
                self.session.refresh(tag)
            existing_link = self.session.exec(
                select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag.id)
            ).first()
            if not existing_link:
                self.session.add(TaskTag(task_id=task_id, tag_id=tag.id))
        self.session.commit()

    def remove_tags(self, task_id: str, tag_names: List[str], user_id: str):
        """Remove specific tags from a task."""
        for name in tag_names:
            tag = self.session.exec(
                select(Tag).where(Tag.user_id == user_id, Tag.name == name)
            ).first()
            if tag:
                link = self.session.exec(
                    select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag.id)
                ).first()
                if link:
                    self.session.delete(link)
        self.session.commit()
