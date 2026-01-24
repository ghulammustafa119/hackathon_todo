"""MCP tool for deleting tasks."""

from typing import Dict, Any
from sqlmodel import Session
from pydantic import BaseModel
from ..services.api_client import backend_client
from ..utils.validation import validate_task_id
from ..utils.logging import log_tool_execution
from .base_tool import BaseMCPTaskTool, ToolResponse


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""
    task_id: str


class DeleteTaskTool(BaseMCPTaskTool):
    """MCP tool for deleting tasks."""

    def __init__(self):
        super().__init__()

    async def execute(self, params: Dict[str, Any], token: str) -> ToolResponse:
        """
        Execute the delete_task tool.

        Args:
            params: Parameters for task deletion
            token: JWT token for authentication

        Returns:
            ToolResponse with deletion confirmation or error
        """
        start_time = __import__('time').time()

        try:
            # Extract parameters
            task_id = params.get("task_id", "").strip()

            # Validate required task_id
            if not validate_task_id(task_id):
                return self._handle_error(
                    "INVALID_TASK_ID",
                    "Valid task ID is required for deletion"
                )

            # Extract user ID from token
            user_id = self._extract_user_id_from_token(token)
            if not user_id:
                return self._handle_error(
                    "AUTHENTICATION_FAILED",
                    "Invalid or expired authentication token"
                )

            # Delete task via backend client
            try:
                delete_response = await backend_client.delete_task(
                    task_id=task_id,
                    token=token
                )

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="delete_task",
                    user_id=user_id,
                    success=True,
                    input_params={"task_id": task_id},
                    output_result={"deleted_task_id": task_id}
                )

                return self._handle_success(
                    data={"task_id": task_id},
                    message="Task deleted successfully"
                )
            except Exception as e:
                # Log failed tool execution
                duration = (__import__('time').time() - start_time) * 1000
                log_tool_execution(
                    tool_name="delete_task",
                    user_id=user_id,
                    success=False,
                    input_params={"task_id": task_id},
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to delete task: {str(e)}"
                )

        except Exception as e:
            # Extract user ID from token for logging if possible
            user_payload = self._validate_jwt(token)
            user_id = user_payload.get("sub") if user_payload else "unknown"

            # Log failed tool execution
            duration = (__import__('time').time() - start_time) * 1000
            log_tool_execution(
                tool_name="delete_task",
                user_id=user_id,
                success=False,
                input_params=params,
                error_details=str(e)
            )

            return self._handle_error(
                "DELETE_TASK_ERROR",
                f"An error occurred while deleting the task: {str(e)}"
            )


# Register the tool
from .registration import tool_registry
delete_task_tool = DeleteTaskTool()
tool_registry.register_tool("delete_task", delete_task_tool)