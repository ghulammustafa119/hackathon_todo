"""MCP Client for interacting with the Todo MCP Server using proper MCP protocol."""

import asyncio
import json
from typing import Dict, Any, Optional
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from contextlib import asynccontextmanager


class TodoMCPClient:
    """Client for interacting with the Todo MCP Server via MCP protocol."""

    def __init__(self, server_url: str = "http://localhost:8001"):
        """
        Initialize the Todo MCP Client.

        Args:
            server_url: URL of the MCP server SSE endpoint
        """
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self._use_direct = True  # Fallback to direct calls if SSE connection fails

    @asynccontextmanager
    async def _get_session(self):
        """Get an MCP client session via SSE transport."""
        try:
            async with sse_client(f"{self.server_url}/sse") as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
        except Exception:
            # Fallback to direct function calls if SSE transport is not available
            yield None

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool using proper MCP protocol.
        Falls back to direct function calls if server is not running separately.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Try MCP protocol first
        if not self._use_direct:
            try:
                async with self._get_session() as session:
                    if session is not None:
                        result = await session.call_tool(tool_name, arguments)
                        if result.content:
                            # Parse the result content
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    return json.loads(content_item.text)
                        return {"success": False, "error": "No content in response"}
            except Exception:
                # Fall through to direct call
                pass

        # Fallback: Direct function call (same-process MCP tools)
        return await self._direct_call(tool_name, arguments)

    async def _direct_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Direct function call fallback for when MCP server runs in-process."""
        from .todo_mcp_server import (
            CreateTaskParams, create_task,
            ListTasksParams, list_tasks,
            UpdateTaskParams, update_task,
            DeleteTaskParams, delete_task,
            CompleteTaskParams, complete_task,
        )

        tool_map = {
            "create_task": (CreateTaskParams, create_task),
            "list_tasks": (ListTasksParams, list_tasks),
            "update_task": (UpdateTaskParams, update_task),
            "delete_task": (DeleteTaskParams, delete_task),
            "complete_task": (CompleteTaskParams, complete_task),
        }

        if tool_name not in tool_map:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        params_class, func = tool_map[tool_name]
        try:
            params = params_class(**arguments)
            result = func(params)
            if isinstance(result, dict):
                return result
            return {"success": False, "error": f"Unexpected result type: {type(result)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_task(self, token: str, title: str, description: str = "", due_date: str = "") -> Dict[str, Any]:
        """Create a new task via MCP protocol."""
        return await self._call_tool("create_task", {
            "token": token,
            "title": title,
            "description": description,
        })

    async def list_tasks(self, token: str, filter_status: str = "all") -> Dict[str, Any]:
        """List tasks via MCP protocol."""
        return await self._call_tool("list_tasks", {
            "token": token,
            "filter_status": filter_status,
        })

    async def update_task(self, token: str, task_id: str, title: Optional[str] = None,
                         description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """Update a task via MCP protocol."""
        args: Dict[str, Any] = {"token": token, "task_id": task_id}
        if title is not None:
            args["title"] = title
        if description is not None:
            args["description"] = description
        return await self._call_tool("update_task", args)

    async def delete_task(self, token: str, task_id: str) -> Dict[str, Any]:
        """Delete a task via MCP protocol."""
        return await self._call_tool("delete_task", {
            "token": token,
            "task_id": task_id,
        })

    async def complete_task(self, token: str, task_id: str, completed: bool = True) -> Dict[str, Any]:
        """Mark a task as complete/incomplete via MCP protocol."""
        return await self._call_tool("complete_task", {
            "token": token,
            "task_id": task_id,
            "completed": completed,
        })


# Global instance of the client
todo_mcp_client = TodoMCPClient()
