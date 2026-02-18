"""MCP tool for setting task priority."""

from typing import Dict, Any, Optional
from ..services.api_client import backend_client
from .base_tool import BaseMCPTaskTool, ToolResponse


class SetPriorityTool(BaseMCPTaskTool):
    """MCP tool for setting task priority."""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "set_priority"

    @property
    def description(self) -> str:
        return "Set the priority of a task (low, medium, high, urgent)"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "The task ID"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            },
            "required": ["task_id", "priority"],
        }

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        if not user_id:
            return self._handle_error("AUTH_ERROR", "User ID required")

        task_id = params.get("task_id")
        priority = params.get("priority")
        if not task_id or not priority:
            return self._handle_error("INVALID_PARAMS", "task_id and priority required")

        if priority not in ("low", "medium", "high", "urgent"):
            return self._handle_error("INVALID_PRIORITY", f"Invalid priority: {priority}")

        try:
            response = await backend_client.put(
                f"/{user_id}/tasks/{task_id}",
                token=token,
                data={"priority": priority},
            )
            if response.get("error"):
                return self._handle_error("UPDATE_FAILED", str(response.get("error")))

            return self._handle_success(
                {"task_id": task_id, "priority": priority},
                f"Priority set to {priority}"
            )
        except Exception as e:
            return self._handle_error("SET_PRIORITY_ERROR", str(e))
