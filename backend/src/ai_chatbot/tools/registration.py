"""MCP tool registration manager."""

from typing import Dict, Type, Callable, Any, Optional
from .base_tool import BaseMCPTaskTool, ToolResponse
from ..utils.logging import agent_logger


class MCPToolRegistry:
    """Registry for managing MCP tools."""

    def __init__(self):
        self._tools: Dict[str, BaseMCPTaskTool] = {}
        self._tool_functions: Dict[str, Callable] = {}

    def register_tool(self, name: str, tool_instance: BaseMCPTaskTool):
        """
        Register an MCP tool instance.

        Args:
            name: Name of the tool
            tool_instance: Instance of the tool to register
        """
        if not isinstance(tool_instance, BaseMCPTaskTool):
            raise TypeError(f"Tool {name} must inherit from BaseMCPTaskTool")

        self._tools[name] = tool_instance
        agent_logger.info(f"Registered MCP tool: {name}")

    def register_tool_function(self, name: str, func: Callable):
        """
        Register a tool as a function.

        Args:
            name: Name of the tool
            func: Function to register as a tool
        """
        self._tool_functions[name] = func
        agent_logger.info(f"Registered MCP tool function: {name}")

    def get_tool(self, name: str) -> BaseMCPTaskTool:
        """
        Get a registered tool by name.

        Args:
            name: Name of the tool to retrieve

        Returns:
            Registered tool instance

        Raises:
            KeyError: If tool is not registered
        """
        if name not in self._tools:
            raise KeyError(f"MCP tool '{name}' not registered")
        return self._tools[name]

    def get_tool_function(self, name: str) -> Callable:
        """
        Get a registered tool function by name.

        Args:
            name: Name of the tool function to retrieve

        Returns:
            Registered tool function

        Raises:
            KeyError: If tool function is not registered
        """
        if name not in self._tool_functions:
            raise KeyError(f"MCP tool function '{name}' not registered")
        return self._tool_functions[name]

    async def execute_tool(self, name: str, params: Dict[str, Any], token: str, user_id: Optional[str] = None) -> Any:
        """
        Execute a registered tool with the given parameters, token, and user ID.

        Args:
            name: Name of the tool to execute
            params: Parameters for the tool execution
            token: JWT token for backend API calls (validated at API level)
            user_id: User ID for authentication (validated at API level)

        Returns:
            Tool execution result
        """
        # Handle the case where user_id is None by providing an empty string
        # since individual tools expect a non-optional string
        effective_user_id = user_id if user_id is not None else ""

        if name in self._tools:
            tool = self._tools[name]
            # Since the tool.execute is async, we need to await it
            result = await tool.execute(params, token, effective_user_id)
            return result
        elif name in self._tool_functions:
            func = self._tool_functions[name]
            result = func(params, token, effective_user_id)
            # If the result is a coroutine (async function), await it
            if hasattr(result, '__await__'):
                return await result
            return result
        else:
            raise KeyError(f"MCP tool '{name}' not found")

    def list_registered_tools(self) -> Dict[str, str]:
        """
        List all registered tools with their types.

        Returns:
            Dictionary mapping tool names to their types
        """
        result = {}
        for name, tool in self._tools.items():
            result[name] = f"{tool.__class__.__module__}.{tool.__class__.__name__}"

        for name, func in self._tool_functions.items():
            result[name] = f"function: {func.__name__}"

        return result

    def unregister_tool(self, name: str):
        """
        Unregister a tool by name.

        Args:
            name: Name of the tool to unregister
        """
        if name in self._tools:
            del self._tools[name]
            agent_logger.info(f"Unregistered MCP tool: {name}")
        elif name in self._tool_functions:
            del self._tool_functions[name]
            agent_logger.info(f"Unregistered MCP tool function: {name}")
        else:
            raise KeyError(f"MCP tool '{name}' not found")


# Global registry instance
tool_registry = MCPToolRegistry()