"""Response formatting utilities for MCP tools."""


def format_task_response(task_data: dict, action: str) -> str:
    """
    Format task response for natural language output.

    Args:
        task_data: Raw task data from backend
        action: Action that was performed (e.g., 'created', 'updated', 'deleted')

    Returns:
        Formatted natural language response
    """
    if not task_data:
        return f"Task {action} successfully."

    title = task_data.get('title', 'Untitled')
    description = task_data.get('description', '')
    completed = task_data.get('completed', False)
    due_date = task_data.get('due_date', '')

    if action == "created":
        response = f"Task '{title}' has been created successfully."
    elif action == "updated":
        response = f"Task '{title}' has been updated successfully."
    elif action == "deleted":
        response = f"Task '{title}' has been deleted successfully."
    elif action == "completed":
        status = "completed" if completed else "marked as incomplete"
        response = f"Task '{title}' has been {status}."
    elif action == "retrieved":
        response = f"Found task: '{title}'"
    else:
        response = f"Task '{title}' has been {action}."

    if description:
        response += f" Description: {description}"

    if due_date:
        response += f" Due date: {due_date}"

    return response


def format_tasks_list_response(tasks_list: list) -> str:
    """
    Format list of tasks for natural language output.

    Args:
        tasks_list: List of task dictionaries from backend

    Returns:
        Formatted natural language response
    """
    if not tasks_list:
        return "No tasks found."

    if len(tasks_list) == 1:
        task = tasks_list[0]
        return format_task_response(task, "retrieved")

    response = f"I found {len(tasks_list)} tasks:\n"
    for i, task in enumerate(tasks_list, 1):
        title = task.get('title', 'Untitled')
        completed = task.get('completed', False)
        due_date = task.get('due_date', '')

        status = "✓" if completed else "○"
        response += f"{i}. [{status}] {title}"

        if due_date:
            response += f" (Due: {due_date})"

        response += "\n"

    return response.rstrip()


def format_error_response(error_code: str, error_message: str) -> str:
    """
    Format error response for natural language output.

    Args:
        error_code: Error code from tool execution
        error_message: Error message from tool execution

    Returns:
        Formatted natural language error response
    """
    # Map specific error codes to user-friendly messages
    error_map = {
        "INVALID_TITLE": "The task title you provided is not valid. Please provide a title with at least one character.",
        "INVALID_DESCRIPTION": "The task description is too long. Please keep it under 1000 characters.",
        "INVALID_DUE_DATE": "The due date format is not valid. Please use YYYY-MM-DD format.",
        "INVALID_TASK_ID": "The task ID you provided is not valid. Please check and try again.",
        "INVALID_STATUS": "The completion status must be either true or false.",
        "AUTHENTICATION_FAILED": "I couldn't authenticate your request. Please make sure you're logged in.",
        "BACKEND_ERROR": "There was an issue with the task service. Please try again later.",
        "CREATE_TASK_ERROR": "I encountered an error while creating the task. Please try again.",
        "LIST_TASKS_ERROR": "I encountered an error while retrieving tasks. Please try again.",
        "UPDATE_TASK_ERROR": "I encountered an error while updating the task. Please try again.",
        "DELETE_TASK_ERROR": "I encountered an error while deleting the task. Please try again.",
        "COMPLETE_TASK_ERROR": "I encountered an error while updating the task completion status. Please try again."
    }

    # Return mapped message if available, otherwise return the original error message
    return error_map.get(error_code, error_message)


def format_confirmation_response(action: str, subject: str) -> str:
    """
    Format confirmation response for user actions.

    Args:
        action: Action that was performed
        subject: Subject of the action

    Returns:
        Formatted natural language confirmation
    """
    return f"I have successfully {action} the {subject} for you."


def format_clarification_request(message: str) -> str:
    """
    Format clarification request for ambiguous inputs.

    Args:
        message: Clarification message

    Returns:
        Formatted natural language clarification request
    """
    return f"I need some clarification: {message}"


def format_general_response(message: str) -> str:
    """
    Format a general response.

    Args:
        message: General message

    Returns:
        Formatted natural language response
    """
    return message