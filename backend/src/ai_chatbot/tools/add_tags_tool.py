"""MCP tool for adding tags to a task."""

from typing import Dict, Any, Optional, List
from ..services.api_client import backend_client
from .base_tool import BaseMCPTaskTool, ToolResponse


class AddTagsTool(BaseMCPTaskTool):
    """MCP tool for adding tags to a task."""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "add_tags"

    @property
    def description(self) -> str:
        return "Add tags to a task"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "The task ID"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags to add"},
            },
            "required": ["task_id", "tags"],
        }

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        if not user_id:
            return self._handle_error("AUTH_ERROR", "User ID required")

        task_id = params.get("task_id")
        tags = params.get("tags", [])
        if not task_id or not tags:
            return self._handle_error("INVALID_PARAMS", "task_id and tags required")

        try:
            response = await backend_client.put(
                f"/{user_id}/tasks/{task_id}",
                token=token,
                data={"tags": tags},
            )
            if response.get("error"):
                return self._handle_error("UPDATE_FAILED", str(response.get("error")))

            return self._handle_success(
                {"task_id": task_id, "tags": tags},
                f"Added tags: {', '.join(tags)}"
            )
        except Exception as e:
            return self._handle_error("ADD_TAGS_ERROR", str(e))
