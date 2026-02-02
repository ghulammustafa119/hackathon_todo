"""Utilities for resolving task references from natural language to actual task IDs."""

import re
from typing import List, Optional, Dict, Any
from ..services.api_client import backend_client
from ..utils.validation import validate_task_id


async def resolve_task_by_title(title_query: str, token: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a task by its title among the user's tasks.

    Args:
        title_query: The title or partial title to search for
        token: JWT token for API authentication
        user_id: User ID for context

    Returns:
        Task dictionary if found, None otherwise
    """
    try:
        # Get all tasks for the user
        response = await backend_client.list_tasks(token=token)
        user_tasks = response.get('tasks', []) if isinstance(response, dict) else []

        # Normalize the search query
        normalized_query = _normalize_search_term(title_query.lower().strip())

        # Search for exact matches first
        for task in user_tasks:
            if task.get('title') and _normalize_search_term(task['title'].lower()) == normalized_query:
                return task

        # Search for partial matches
        for task in user_tasks:
            if task.get('title') and normalized_query in _normalize_search_term(task['title'].lower()):
                return task

        # Search by description if no title match found
        for task in user_tasks:
            if task.get('description') and normalized_query in task['description'].lower():
                return task

        return None
    except Exception as e:
        print(f"Error resolving task by title: {str(e)}")
        return None


async def resolve_tasks_by_title(title_query: str, token: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Find all tasks that match a title query.

    Args:
        title_query: The title or partial title to search for
        token: JWT token for API authentication
        user_id: User ID for context

    Returns:
        List of matching task dictionaries
    """
    try:
        # Get all tasks for the user
        response = await backend_client.list_tasks(token=token)
        user_tasks = response.get('tasks', []) if isinstance(response, dict) else []

        # Normalize the search query
        normalized_query = _normalize_search_term(title_query.lower().strip())

        matching_tasks = []

        # Search for matches in title
        for task in user_tasks:
            if task.get('title'):
                if normalized_query == _normalize_search_term(task['title'].lower()):
                    # Exact match gets priority
                    matching_tasks.insert(0, task)
                elif normalized_query in _normalize_search_term(task['title'].lower()):
                    # Partial match goes at end
                    matching_tasks.append(task)

        # Also search in description if no title matches found
        if not matching_tasks:
            for task in user_tasks:
                if task.get('description') and normalized_query in task['description'].lower():
                    matching_tasks.append(task)

        return matching_tasks
    except Exception as e:
        print(f"Error resolving tasks by title: {str(e)}")
        return []


def _normalize_search_term(term: str) -> str:
    """
    Normalize search terms for comparison.

    Args:
        term: The term to normalize

    Returns:
        Normalized term
    """
    # Remove common articles and prepositions for better matching
    term = re.sub(r'\b(a|an|the|and|or|but|in|on|at|to|for|of|with|by)\b', '', term)
    # Remove extra whitespace
    term = ' '.join(term.split())
    return term


def format_task_list_for_user(tasks: List[Dict[str, Any]]) -> str:
    """
    Format a list of tasks for user display.

    Args:
        tasks: List of task dictionaries

    Returns:
        Formatted string for user
    """
    if not tasks:
        return "No tasks found."

    result = "Here are the matching tasks:\n"
    for i, task in enumerate(tasks, 1):
        status = "✓" if task.get('completed', False) else "○"
        result += f"{i}. [{status}] {task.get('title', 'Untitled')} (ID: {task.get('id', 'N/A')})\n"

    result += "\nPlease specify which task you'd like to delete by number or ID."
    return result