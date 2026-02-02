"""Utility functions for parameter validation and sanitization."""

import re
from datetime import datetime
from typing import Any, Dict, Optional
from sqlmodel import Session, select
from src.models.task import Task


def validate_task_title(title: str) -> bool:
    """
    Validate task title.

    Args:
        title: The task title to validate

    Returns:
        True if valid, False otherwise
    """
    if not title or len(title.strip()) == 0:
        return False

    if len(title) > 255:  # Reasonable length limit
        return False

    return True


def validate_task_description(description: str) -> bool:
    """
    Validate task description.

    Args:
        description: The task description to validate

    Returns:
        True if valid, False otherwise
    """
    if description is None:
        return True  # Description is optional

    if len(description) > 1000:  # Reasonable length limit
        return False

    return True


def validate_task_due_date(due_date: str) -> bool:
    """
    Validate task due date format (ISO 8601).

    Args:
        due_date: The due date string to validate

    Returns:
        True if valid, False otherwise
    """
    if due_date is None:
        return True  # Due date is optional

    try:
        # Attempt to parse the date in ISO 8601 format (YYYY-MM-DD)
        datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def validate_task_id(task_id: str) -> bool:
    """
    Validate task ID format.

    Args:
        task_id: The task ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not task_id:
        return False

    # UUID format validation (simplified)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, task_id))


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input string by removing potentially harmful content.

    Args:
        input_str: The input string to sanitize

    Returns:
        Sanitized string
    """
    if not input_str:
        return input_str

    # Remove potentially harmful characters/sequences
    sanitized = input_str.strip()

    # Prevent SQL injection attempts by removing certain patterns
    # This is a basic example - in production, use proper parameterized queries
    sanitized = re.sub(r'[;\'"\\]', '', sanitized)

    return sanitized


def validate_user_ownership(
    session: Session,
    task_id: str,
    user_id: str
) -> bool:
    """
    Validate that the task belongs to the user.

    Args:
        session: Database session
        task_id: ID of the task to check
        user_id: ID of the user making the request

    Returns:
        True if user owns the task, False otherwise
    """
    # Query the task by ID
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if not task:
        return False

    return task.user_id == user_id


def validate_task_status(status: bool) -> bool:
    """
    Validate task completion status.

    Args:
        status: The status value to validate

    Returns:
        True if valid, False otherwise
    """
    if status is None:
        return True  # Status is optional for some operations

    return isinstance(status, bool)