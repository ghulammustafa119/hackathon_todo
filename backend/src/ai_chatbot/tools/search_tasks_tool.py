"""MCP tool for searching tasks by keyword, priority, or tag."""

from typing import Dict, Any, Optional
from ..services.api_client import backend_client
from .base_tool import BaseMCPTaskTool, ToolResponse


class SearchTasksTool(BaseMCPTaskTool):
    """MCP tool for searching tasks."""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "search_tasks"

    @property
    def description(self) -> str:
        return "Search tasks by keyword, priority, status, or tag"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword for title/description"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "status": {"type": "string", "enum": ["pending", "completed"]},
                "tag": {"type": "string", "description": "Filter by tag name"},
            },
        }

    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        if not user_id:
            return self._handle_error("AUTH_ERROR", "User ID required")

        try:
            query_params = {}
            if params.get("query"):
                query_params["search"] = params["query"]
            if params.get("priority"):
                query_params["priority"] = params["priority"]
            if params.get("status"):
                query_params["status"] = params["status"]
            if params.get("tag"):
                query_params["tag"] = params["tag"]

            qs = "&".join(f"{k}={v}" for k, v in query_params.items())
            endpoint = f"/{user_id}/tasks"
            if qs:
                endpoint += f"?{qs}"

            response = await backend_client.get(endpoint, token=token)

            if response.get("error"):
                return self._handle_error("SEARCH_FAILED", str(response.get("error")))

            tasks = response if isinstance(response, list) else response.get("data", [])
            return self._handle_success(
                {"tasks": tasks, "count": len(tasks)},
                f"Found {len(tasks)} task(s)"
            )
        except Exception as e:
            return self._handle_error("SEARCH_ERROR", str(e))
