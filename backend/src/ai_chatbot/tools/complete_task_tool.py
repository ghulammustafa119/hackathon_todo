"""MCP tool for completing tasks."""

from typing import Dict, Any
from sqlmodel import Session
from pydantic import BaseModel
from ..services.api_client import backend_client
from ..utils.validation import validate_task_id, validate_task_status
from ..utils.logging import log_tool_execution
from .base_tool import BaseMCPTaskTool, ToolResponse


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool."""
    task_id: str
    completed: bool


class CompleteTaskTool(BaseMCPTaskTool):
    """MCP tool for completing tasks."""

    def __init__(self):
        super().__init__()

    async def execute(self, params: Dict[str, Any], token: str) -> ToolResponse:
        """
        Execute the complete_task tool.

        Args:
            params: Parameters for task completion
            token: JWT token for authentication

        Returns:
            ToolResponse with updated task data or error
        """
        start_time = __import__('time').time()

        try:
            # Extract parameters
            task_id = params.get("task_id", "").strip()
            completed = params.get("completed")

            # Validate required parameters
            if not validate_task_id(task_id):
                return self._handle_error(
                    "INVALID_TASK_ID",
                    "Valid task ID is required for completion"
                )

            if completed is None:
                return self._handle_error(
                    "INVALID_COMPLETED",
                    "Completion status (true/false) is required"
                )

            if not validate_task_status(completed):
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

            # Update task completion status via backend client
            try:
                updated_task = await backend_client.toggle_task_completion(
                    task_id=task_id,
                    completed=completed,
                    token=token
                )

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="complete_task",
                    user_id=user_id,
                    success=True,
                    input_params={"task_id": task_id, "completed": completed},
                    output_result=updated_task
                )

                return self._handle_success(
                    data=updated_task,
                    message=f"Task marked as {'completed' if completed else 'incomplete'} successfully"
                )
            except Exception as e:
                # Log failed tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="complete_task",
                    user_id=user_id,
                    success=False,
                    input_params={"task_id": task_id, "completed": completed},
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to update task completion status: {str(e)}"
                )

        except Exception as e:
            # Extract user ID from token for logging if possible
            user_payload = self._validate_jwt(token)
            user_id = user_payload.get("sub") if user_payload else "unknown"

            # Log failed tool execution
            duration = (__import__('time').time() - start_time) * 1000
            log_tool_execution(
                tool_name="complete_task",
                user_id=user_id,
                success=False,
                input_params=params,
                error_details=str(e)
            )

            return self._handle_error(
                "COMPLETE_TASK_ERROR",
                f"An error occurred while updating task completion: {str(e)}"
            )


# Register the tool
from .registration import tool_registry
complete_task_tool = CompleteTaskTool()
tool_registry.register_tool("complete_task", complete_task_tool)