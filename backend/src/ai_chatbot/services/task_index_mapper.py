"""Service for mapping task indices to actual task IDs based on conversation history."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import threading


class TaskIndexMapper:
    """Manages the mapping between task indices (from list view) and actual task IDs."""

    def __init__(self):
        self._task_mappings: Dict[str, Dict[int, str]] = {}  # user_id -> {index -> task_id}
        self._last_task_lists: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> list of tasks
        self._last_access_times: Dict[str, datetime] = {}  # user_id -> last access time
        self._most_recent_task_ids: Dict[str, str] = {}  # user_id -> most recent task_id
        self._lock = threading.Lock()  # Thread safety for concurrent access

    def store_task_list(self, user_id: str, tasks: List[Dict[str, Any]]):
        """
        Store the current task list and create index -> task_id mapping.

        Args:
            user_id: User ID
            tasks: List of task dictionaries
        """
        with self._lock:
            self._last_task_lists[user_id] = tasks
            self._task_mappings[user_id] = {}

            # Create mapping: index (1-based) -> task_id
            for idx, task in enumerate(tasks):
                self._task_mappings[user_id][idx + 1] = task.get('id', '')

            self._last_access_times[user_id] = datetime.now(timezone.utc)

    def get_task_id_by_index(self, user_id: str, index: int) -> Optional[str]:
        """
        Get the actual task ID by its index in the last list.

        Args:
            user_id: User ID
            index: Task index (1-based)

        Returns:
            Task ID if found, None otherwise
        """
        with self._lock:
            # Check if we have a mapping for this user
            if user_id not in self._task_mappings:
                return None

            # Check if the mapping is still valid (less than 10 minutes old)
            if datetime.now(timezone.utc) - self._last_access_times[user_id] > timedelta(minutes=10):
                # Clean up old mapping
                del self._task_mappings[user_id]
                if user_id in self._last_task_lists:
                    del self._last_task_lists[user_id]
                if user_id in self._last_access_times:
                    del self._last_access_times[user_id]
                return None

            # Return the task ID for the given index
            return self._task_mappings[user_id].get(index)

    def has_recent_task_list(self, user_id: str) -> bool:
        """
        Check if we have a recent task list for the user.

        Args:
            user_id: User ID

        Returns:
            True if we have a recent task list, False otherwise
        """
        with self._lock:
            if user_id not in self._last_access_times:
                return False

            # Check if older than 10 minutes
            if datetime.now(timezone.utc) - self._last_access_times[user_id] > timedelta(minutes=10):
                # Clean up old data
                if user_id in self._task_mappings:
                    del self._task_mappings[user_id]
                if user_id in self._last_task_lists:
                    del self._last_task_lists[user_id]
                if user_id in self._last_access_times:
                    del self._last_access_times[user_id]
                return False

            return True

    def get_last_task_list(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get the last stored task list for the user.

        Args:
            user_id: User ID

        Returns:
            Last task list if available, empty list otherwise
        """
        with self._lock:
            if user_id not in self._last_task_lists:
                return []

            # Check if the list is still valid
            if datetime.now(timezone.utc) - self._last_access_times[user_id] > timedelta(minutes=10):
                # Clean up old data
                if user_id in self._task_mappings:
                    del self._task_mappings[user_id]
                if user_id in self._last_task_lists:
                    del self._last_task_lists[user_id]
                if user_id in self._last_access_times:
                    del self._last_access_times[user_id]
                return []

            return self._last_task_lists[user_id]

    def set_most_recent_task_id(self, user_id: str, task_id: str):
        """
        Set the most recent task ID for a user.

        Args:
            user_id: User ID
            task_id: The task ID to set as most recent
        """
        with self._lock:
            self._most_recent_task_ids[user_id] = task_id

    def get_most_recent_task_id(self, user_id: Optional[str]) -> Optional[str]:
        """
        Get the most recent task ID for a user.

        Args:
            user_id: User ID

        Returns:
            Most recent task ID if available, None otherwise
        """
        if not user_id:
            return None

        with self._lock:
            return self._most_recent_task_ids.get(user_id)


# Global instance
task_index_mapper = TaskIndexMapper()