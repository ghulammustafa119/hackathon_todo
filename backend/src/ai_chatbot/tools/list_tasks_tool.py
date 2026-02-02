"""MCP tool for listing tasks."""

from typing import Dict, Any, Optional
from sqlmodel import Session
from pydantic import BaseModel
from ..services.api_client import backend_client
from ..utils.validation import sanitize_input
from ..utils.logging import log_tool_execution
from .base_tool import BaseMCPTaskTool, ToolResponse


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    filter: str = "all"
    limit: int = 100
    search_query: str = ""


class ListTasksTool(BaseMCPTaskTool):
    """MCP tool for listing tasks."""

    def __init__(self):
        super().__init__()

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        """
        Execute the list_tasks tool.

        Args:
            params: Parameters for task listing
            token: JWT token for backend API calls (already validated at API level)
            user_id: User ID for authentication (already validated at API level)

        Returns:
            ToolResponse with list of tasks or error
        """
        start_time = __import__('time').time()

        try:
            # Extract and sanitize parameters
            filter_param = params.get("filter", "all")
            limit = params.get("limit", 100)
            search_query = sanitize_input(params.get("search_query", "").strip())

            # Validate filter parameter
            valid_filters = ["all", "pending", "completed"]
            if filter_param not in valid_filters:
                filter_param = "all"  # Default to all

            # Validate limit parameter
            try:
                limit = int(limit)
                if limit <= 0:
                    limit = 100  # Default to 100
                elif limit > 100:
                    limit = 100  # Cap at 100
            except (ValueError, TypeError):
                limit = 100  # Default to 100

            # List tasks via backend client
            try:
                tasks_response = await backend_client.list_tasks(
                    filter_param=filter_param,
                    limit=limit,
                    search_query=search_query if search_query else None,
                    token=token  # Use the token passed from the API layer
                )

                # Log successful tool execution
                duration = (__import__('time').time() - start_time) * 1000

                # Handle both dict and list responses from the backend
                if isinstance(tasks_response, dict):
                    task_count = len(tasks_response.get("tasks", []))
                elif isinstance(tasks_response, list):
                    task_count = len(tasks_response)
                    # Convert list response to expected dict format
                    tasks_response = {"tasks": tasks_response}
                else:
                    task_count = 0

                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="list_tasks",
                    user_id=safe_user_id,
                    success=True,
                    input_params={
                        "filter": filter_param,
                        "limit": limit,
                        "search_query": search_query
                    },
                    output_result={"task_count": task_count}
                )

                return self._handle_success(
                    data=tasks_response,
                    message="Tasks retrieved successfully"
                )
            except Exception as e:
                # Log failed tool execution
                duration = (__import__('time').time() - start_time) * 1000
                safe_user_id = user_id if user_id is not None else "unknown"
                log_tool_execution(
                    tool_name="list_tasks",
                    user_id=safe_user_id,
                    success=False,
                    input_params={
                        "filter": filter_param,
                        "limit": limit,
                        "search_query": search_query
                    },
                    error_details=str(e)
                )

                return self._handle_error(
                    "BACKEND_ERROR",
                    f"Failed to retrieve tasks: {str(e)}"
                )

        except Exception as e:
            # Log failed tool execution - user_id is already available from the method parameter
            duration = (__import__('time').time() - start_time) * 1000
            safe_user_id = user_id if user_id is not None else "unknown"
            log_tool_execution(
                tool_name="list_tasks",
                user_id=safe_user_id,
                success=False,
                input_params=params,
                error_details=str(e)
            )

            return self._handle_error(
                "LIST_TASKS_ERROR",
                f"An error occurred while listing tasks: {str(e)}"
            )


# Register the tool
from .registration import tool_registry
list_tasks_tool = ListTasksTool()
tool_registry.register_tool("list_tasks", list_tasks_tool)