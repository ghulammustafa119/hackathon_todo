"""MCP tool for completing tasks."""

from typing import Dict, Any, Optional
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

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        """
        Execute the complete_task tool.

        Args:
            params: Parameters for task completion
            token: JWT token for backend API calls (already validated at API level)
            user_id: User ID for authentication (already validated at API level)

        Returns:
            ToolResponse with updated task data or error
        """
        start_time = __import__('time').time()

        try:
            # Extract parameters
            task_id = params.get("task_id", "")

            # Convert to string if it's not already a string (e.g., if AI sends it as int)
            if task_id is None:
                task_id = ""
            elif not isinstance(task_id, str):
                task_id = str(task_id)

            task_id = task_id.strip()
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

            # Update task completion status via backend client
            try:
                response = await backend_client.toggle_task_completion(
                    task_id=task_id,
                    completed=completed,
                    token=token  # Use the token passed from the API layer
                )

                # The response from toggle_task_completion contains id and completed status
                # Get the full task details to provide complete information back
                updated_task = await backend_client.get_task(task_id=task_id, token=token)

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000
                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="complete_task",
                    user_id=safe_user_id,
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
                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="complete_task",
                    user_id=safe_user_id,
                    success=False,
                    input_params={"task_id": task_id, "completed": completed},
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to update task completion status: {str(e)}"
                )

        except Exception as e:
            # Log failed tool execution - user_id is already available from the method parameter
            duration = (__import__('time').time() - start_time) * 1000
            safe_user_id = user_id if user_id is not None else "unknown"
            log_tool_execution(
                tool_name="complete_task",
                user_id=safe_user_id,
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