"""MCP tool for setting a task's due date."""

from typing import Dict, Any, Optional
from ..services.api_client import backend_client
from .base_tool import BaseMCPTaskTool, ToolResponse


class SetDueDateTool(BaseMCPTaskTool):
    """MCP tool for setting a task's due date."""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "set_due_date"

    @property
    def description(self) -> str:
        return "Set or update the due date of a task"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "The task ID"},
                "due_date": {"type": "string", "description": "Due date in ISO format (e.g., 2026-02-20T14:00:00)"},
            },
            "required": ["task_id", "due_date"],
        }

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        if not user_id:
            return self._handle_error("AUTH_ERROR", "User ID required")

        task_id = params.get("task_id")
        due_date = params.get("due_date")
        if not task_id or not due_date:
            return self._handle_error("INVALID_PARAMS", "task_id and due_date required")

        try:
            response = await backend_client.put(
                f"/{user_id}/tasks/{task_id}",
                token=token,
                data={"due_date": due_date},
            )
            if response.get("error"):
                return self._handle_error("UPDATE_FAILED", str(response.get("error")))

            return self._handle_success(
                {"task_id": task_id, "due_date": due_date},
                f"Due date set to {due_date}"
            )
        except Exception as e:
            return self._handle_error("SET_DUE_DATE_ERROR", str(e))
