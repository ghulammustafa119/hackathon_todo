"""Task CRUD operations service for Phase I console app
Contract: specs/001-phase1-console-app/contracts/operations.py
"""

from typing import Dict, List
from .storage import TaskStorage


class TaskOperations:
    """Business logic layer coordinating task CRUD operations"""

    def __init__(self, storage: TaskStorage):
        """
        Initialize operations with storage dependency

        Args:
            storage: Instance of TaskStorage service
        """
        self.storage = storage

    def create_task(self, title: str, description: str = None) -> dict:
        """
        Create a new task with validation and ID assignment

        Args:
            title: Non-empty task title
            description: Optional task description details

        Returns:
            dict with keys:
            - success (bool): True if task created, False if validation failed
            - task_id (int): Assigned task ID (only if success=True)
            - task (dict): Created task data (only if success=True)
            - error (str | None): Error message (only if success=False)
        """
        # Validate title
        if not title or not title.strip():
            return {"success": False, "error": "Title cannot be empty"}

        # Create task
        try:
            task_id = self.storage.create(title, description)
            task = self.storage.get(task_id)
            return {"success": True, "task_id": task_id, "task": task}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def update_task(self, task_id: int, title: str = None, description: str = None) -> dict:
        """
        Update an existing task's title and/or description

        Args:
            task_id: Unique identifier of task to update
            title: Optional new title value
            description: Optional new description value

        Returns:
            dict with keys:
            - success (bool): True if task updated, False if validation failed or not found
            - updated_task (dict): Updated task data (only if success=True)
            - error (str | None): Error message (only if success=False)
        """
        # Validate task_id
        if not self.storage.exists(task_id):
            return {"success": False, "error": "Task not found"}

        # Validate at least one field provided
        if not title and not description:
            return {"success": False, "error": "At least one field must be provided"}

        # Update task
        success = self.storage.update(task_id, title=title, description=description)
        if not success:
            return {"success": False, "error": "Update failed"}

        task = self.storage.get(task_id)
        return {"success": True, "updated_task": task}

    def delete_task(self, task_id: int) -> dict:
        """
        Delete a task from storage

        Args:
            task_id: Unique identifier of task to delete

        Returns:
            dict with keys:
            - success (bool): True if task deleted, False if not found
            - deleted_task_id (int): Deleted task ID (only if success=True)
            - error (str | None): Error message (only if success=False)
        """
        # Validate task_id
        if not self.storage.exists(task_id):
            return {"success": False, "error": "Task not found"}

        # Delete task
        success = self.storage.delete(task_id)
        if not success:
            return {"success": False, "error": "Deletion failed"}

        return {"success": True, "deleted_task_id": task_id}

    def toggle_completion(self, task_id: int) -> dict:
        """
        Toggle task completion status between false and true

        Args:
            task_id: Unique identifier of task to toggle

        Returns:
            dict with keys:
            - success (bool): True if task toggled, False if not found
            - updated_task (dict): Updated task data (only if success=True)
            - old_status (bool): Previous completion status (only if success=True)
            - new_status (bool): New completion status (only if success=True)
            - error (str | None): Error message (only if success=False)
        """
        # Validate task_id
        if not self.storage.exists(task_id):
            return {"success": False, "error": "Task not found"}

        # Get current task
        task = self.storage.get(task_id)
        old_status = task.completed

        # Toggle completion
        new_status = not old_status
        self.storage.update(task_id, completed=new_status)

        updated_task = self.storage.get(task_id)
        return {
            "success": True,
            "old_status": old_status,
            "new_status": new_status,
            "updated_task": updated_task
        }

    def list_tasks(self) -> dict:
        """
        Retrieve all tasks for display

        Args:
            None

        Returns:
            dict with keys:
            - success (bool): Always True (list operation always succeeds)
            - tasks (list): List of all task dicts
            - count (int): Number of tasks in storage
        """
        tasks = self.storage.get_all()
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
