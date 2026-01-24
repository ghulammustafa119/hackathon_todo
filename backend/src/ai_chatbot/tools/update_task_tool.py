"""MCP tool for updating tasks."""

from typing import Dict, Any
from sqlmodel import Session
from pydantic import BaseModel
from ..services.api_client import backend_client
from ..utils.validation import (
    validate_task_id,
    validate_task_title,
    validate_task_description,
    validate_task_due_date,
    validate_task_status,
    sanitize_input
)
from ..utils.logging import log_tool_execution
from .base_tool import BaseMCPTaskTool, ToolResponse


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    task_id: str
    title: str = ""
    description: str = ""
    due_date: str = ""
    completed: bool = None


class UpdateTaskTool(BaseMCPTaskTool):
    """MCP tool for updating tasks."""

    def __init__(self):
        super().__init__()

    async def execute(self, params: Dict[str, Any], token: str) -> ToolResponse:
        """
        Execute the update_task tool.

        Args:
            params: Parameters for task update
            token: JWT token for authentication

        Returns:
            ToolResponse with updated task data or error
        """
        start_time = __import__('time').time()

        try:
            # Extract and sanitize parameters
            task_id = params.get("task_id", "").strip()
            title = sanitize_input(params.get("title", "").strip())
            description = sanitize_input(params.get("description", "").strip())
            due_date = params.get("due_date", "").strip()
            completed = params.get("completed")

            # Validate required task_id
            if not validate_task_id(task_id):
                return self._handle_error(
                    "INVALID_TASK_ID",
                    "Valid task ID is required for update"
                )

            # Validate optional parameters if provided
            if title and not validate_task_title(title):
                return self._handle_error(
                    "INVALID_TITLE",
                    "Task title is invalid"
                )

            if description and not validate_task_description(description):
                return self._handle_error(
                    "INVALID_DESCRIPTION",
                    "Task description is too long"
                )

            if due_date and not validate_task_due_date(due_date):
                return self._handle_error(
                    "INVALID_DUE_DATE",
                    "Due date format is invalid. Use ISO 8601 format (YYYY-MM-DD)"
                )

            if completed is not None and not validate_task_status(completed):
                return self._handle_error(
                    "INVALID_STATUS",
                    "Task completion status must be a boolean value"
                )

            # Extract user ID from token
            user_id = self._extract_user_id_from_token(token)
            if not user_id:
                return self._handle_error(
                    "AUTHENTICATION_FAILED",
                    "Invalid or expired authentication token"
                )

            # Update task via backend client
            try:
                updated_task = await backend_client.update_task(
                    task_id=task_id,
                    title=title if title else None,
                    description=description if description else None,
                    due_date=due_date if due_date else None,
                    completed=completed if completed is not None else None,
                    token=token
                )

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="update_task",
                    user_id=user_id,
                    success=True,
                    input_params={
                        "task_id": task_id,
                        "title": title,
                        "description": description,
                        "due_date": due_date,
                        "completed": completed
                    },
                    output_result=updated_task
                )

                return self._handle_success(
                    data=updated_task,
                    message="Task updated successfully"
                )
            except Exception as e:
                # Log failed tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="update_task",
                    user_id=user_id,
                    success=False,
                    input_params={
                        "task_id": task_id,
                        "title": title,
                        "description": description,
                        "due_date": due_date,
                        "completed": completed
                    },
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to update task: {str(e)}"
                )

        except Exception as e:
            # Extract user ID from token for logging if possible
            user_payload = self._validate_jwt(token)
            user_id = user_payload.get("sub") if user_payload else "unknown"

            # Log failed tool execution
            duration = (__import__('time').time() - start_time) * 1000
            log_tool_execution(
                tool_name="update_task",
                user_id=user_id,
                success=False,
                input_params=params,
                error_details=str(e)
            )

            return self._handle_error(
                "UPDATE_TASK_ERROR",
                f"An error occurred while updating the task: {str(e)}"
            )


# Register the tool
from .registration import tool_registry
update_task_tool = UpdateTaskTool()
tool_registry.register_tool("update_task", update_task_tool)