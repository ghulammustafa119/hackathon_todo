"""In-memory task storage service for Phase I console app
Contract: specs/001-phase1-console-app/contracts/storage.py
"""

from typing import Dict, List, Optional
from ..models.task import Task


class TaskStorage:
    """Manages in-memory storage of tasks with unique integer IDs"""

    def __init__(self):
        """Initialize empty in-memory task storage"""
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1

    def create(self, title: str, description: str = None) -> int:
        """
        Create a new task with specified title and optional description

        Args:
            title: Non-empty task title
            description: Optional task description

        Returns:
            int: Unique task ID assigned to created task

        Raises:
            ValueError: If title is empty or whitespace only
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(
            id=self.next_id,
            title=title.strip(),
            description=description,
            completed=False
        )
        self.tasks[self.next_id] = task
        task_id = self.next_id
        self.next_id += 1
        return task_id

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a single task by ID

        Args:
            task_id: Unique identifier of task to retrieve

        Returns:
            Task | None: Task dict if found, None if not found
        """
        return self.tasks.get(task_id)

    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks in storage

        Returns:
            List[Task]: List of all task dicts
        """
        return list(self.tasks.values())

    def update(self, task_id: int, **kwargs) -> bool:
        """
        Update an existing task's title and/or description

        Args:
            task_id: Unique identifier of task to update
            **kwargs: Keyword arguments for fields to update (title, description)

        Returns:
            bool: True if update succeeded, False if task not found

        Side Effects:
            Updates task in storage
            Does NOT modify task.completed status
        """
        task = self.tasks.get(task_id)
        if not task:
            return False

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return True

    def delete(self, task_id: int) -> bool:
        """
        Delete a task from storage

        Args:
            task_id: Unique identifier of task to delete

        Returns:
            bool: True if deletion succeeded, False if task not found
        """
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        return True

    def exists(self, task_id: int) -> bool:
        """
        Check if a task ID exists in storage

        Args:
            task_id: Unique identifier to check

        Returns:
            bool: True if task exists, False if not found
        """
        return task_id in self.tasks
