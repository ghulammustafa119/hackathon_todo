"""MCP tool for creating tasks."""

from typing import Dict, Any, Optional
from sqlmodel import Session
from pydantic import BaseModel
from ..services.api_client import backend_client
from ..utils.validation import (
    validate_task_title,
    validate_task_description,
    validate_task_due_date,
    sanitize_input
)
from ..utils.logging import log_tool_execution
from .base_tool import BaseMCPTaskTool, ToolResponse
from ..config import config


class CreateTaskParams(BaseModel):
    """Parameters for create_task tool."""
    title: str
    description: str = ""
    due_date: str = ""


class CreateTaskTool(BaseMCPTaskTool):
    """MCP tool for creating tasks."""

    def __init__(self):
        super().__init__()

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        """
        Execute the create_task tool.

        Args:
            params: Parameters for task creation
            token: JWT token for backend API calls (already validated at API level)
            user_id: User ID for authentication (already validated at API level)

        Returns:
            ToolResponse with created task data or error
        """
        start_time = __import__('time').time()

        try:
            # Extract and sanitize parameters
            title = sanitize_input(params.get("title", "").strip())
            description = sanitize_input(params.get("description", "").strip())
            due_date = params.get("due_date", "").strip()

            # Validate parameters
            if not validate_task_title(title):
                return self._handle_error(
                    "INVALID_TITLE",
                    "Task title is required and must be valid"
                )

            if not validate_task_description(description):
                return self._handle_error(
                    "INVALID_DESCRIPTION",
                    "Task description is too long"
                )

            if due_date and not validate_task_due_date(due_date):
                return self._handle_error(
                    "INVALID_DUE_DATE",
                    "Due date format is invalid. Use ISO 8601 format (YYYY-MM-DD)"
                )

            # Create task via backend client - pass user_id for logging purposes
            try:
                # Use the token for actual API calls since authentication still happens at HTTP level
                created_task = await backend_client.create_task(
                    title=title,
                    description=description if description else None,
                    due_date=due_date if due_date else None,
                    token=token  # Use the token passed from the API layer
                )

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000
                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="create_task",
                    user_id=safe_user_id,
                    success=True,
                    input_params={"title": title, "description": description, "due_date": due_date},
                    output_result=created_task
                )

                return self._handle_success(
                    data=created_task,
                    message="Task created successfully"
                )
            except Exception as e:
                # Log failed tool execution
                duration = (__import__('time').time() - start_time) * 1000
                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="create_task",
                    user_id=safe_user_id,
                    success=False,
                    input_params={"title": title, "description": description, "due_date": due_date},
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to create task: {str(e)}"
                )

        except Exception as e:
            # Log failed tool execution - user_id is already available from the method parameter
            duration = (__import__('time').time() - start_time) * 1000
            safe_user_id = user_id if user_id is not None else "unknown"
            log_tool_execution(
                tool_name="create_task",
                user_id=safe_user_id,
                success=False,
                input_params=params,
                error_details=str(e)
            )

            return self._handle_error(
                "CREATE_TASK_ERROR",
                f"An error occurred while creating the task: {str(e)}"
            )


# Register the tool
from .registration import tool_registry
create_task_tool = CreateTaskTool()
tool_registry.register_tool("create_task", create_task_tool)