"""Tool chaining for multi-step operations."""

from typing import List, Dict, Any, Optional
from ..tools.registration import tool_registry
from ..utils.response_formatter import format_error_response
from ..utils.logging import agent_logger


class ToolChainExecutor:
    """Handles execution of multiple tools in sequence for complex operations."""

    def __init__(self):
        # DISABLED (Phase III): Conversation memory is disabled to comply with
        # the Stateless System Rule. Deferred to Phase V.
        self.max_steps = 5  # Prevent infinite loops

    async def execute_chain(
        self,
        tool_calls: List[Dict[str, Any]],
        token: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a chain of tool calls sequentially.

        Args:
            tool_calls: List of tool call dictionaries
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Dictionary with success status and results
        """
        results = []
        context = {}

        for i, tool_call in enumerate(tool_calls):
            if i >= self.max_steps:
                error_msg = f"Tool chain exceeded maximum steps ({self.max_steps})"
                agent_logger.warning(
                    error_msg,
                    context={"step_count": i},
                    user_id=user_id
                )
                return {
                    "success": False,
                    "error": error_msg,
                    "partial_results": results
                }

            function_name = tool_call.get("name", tool_call.get("function", {}).get("name"))
            function_args = tool_call.get("arguments", tool_call.get("function", {}).get("arguments", {}))

            # If arguments is a string, parse it as JSON
            if isinstance(function_args, str):
                import json
                try:
                    function_args = json.loads(function_args)
                except json.JSONDecodeError:
                    error_msg = f"Invalid JSON arguments for tool {function_name}"
                    agent_logger.error(
                        error_msg,
                        context={"raw_arguments": function_args},
                        user_id=user_id
                    )
                    return {
                        "success": False,
                        "error": error_msg,
                        "partial_results": results
                    }

            # Update arguments with context from previous steps if needed
            updated_args = self._update_args_with_context(function_args, context)

            try:
                # Execute the tool
                tool_response = await tool_registry.execute_tool(function_name, updated_args, token)

                # Store result
                result = {
                    "tool": function_name,
                    "input": updated_args,
                    "output": tool_response,
                    "success": tool_response.success
                }
                results.append(result)

                # Update context for subsequent steps
                context = self._update_context(context, function_name, tool_response)

                # If any tool fails, decide whether to continue or stop
                if not tool_response.success:
                    agent_logger.warning(
                        f"Tool {function_name} failed in chain",
                        context={"step": i, "error": tool_response.error},
                        user_id=user_id
                    )

                    # For now, we continue execution even if a step fails
                    # In the future, we might want to implement conditional chaining

            except Exception as e:
                error_msg = f"Error executing tool {function_name} in chain: {str(e)}"
                agent_logger.error(
                    error_msg,
                    context={"step": i, "function_name": function_name},
                    user_id=user_id
                )

                result = {
                    "tool": function_name,
                    "input": updated_args,
                    "output": None,
                    "success": False,
                    "error": str(e)
                }
                results.append(result)

        return {
            "success": True,
            "results": results,
            "context": context
        }

    def _update_args_with_context(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update tool arguments with context from previous steps.

        Args:
            args: Original arguments
            context: Context from previous steps

        Returns:
            Updated arguments
        """
        updated_args = args.copy()

        # If an ID is needed but not provided, try to get it from context
        if 'task_id' in updated_args and not updated_args['task_id']:
            if 'last_created_task_id' in context:
                updated_args['task_id'] = context['last_created_task_id']

        # Add other context-based updates as needed
        # For example, if a tool needs user preferences, etc.

        return updated_args

    def _update_context(
        self,
        context: Dict[str, Any],
        function_name: str,
        tool_response: Any
    ) -> Dict[str, Any]:
        """
        Update context based on tool response.

        Args:
            context: Current context
            function_name: Name of the function that was executed
            tool_response: Response from the tool

        Returns:
            Updated context
        """
        new_context = context.copy()

        # Store relevant information based on the tool executed
        if function_name == "create_task" and tool_response.success:
            if hasattr(tool_response, 'data') and tool_response.data:
                task_data = tool_response.data.get('task') or tool_response.data
                if isinstance(task_data, dict) and 'id' in task_data:
                    new_context['last_created_task_id'] = task_data['id']

        elif function_name == "list_tasks" and tool_response.success:
            if hasattr(tool_response, 'data') and tool_response.data:
                tasks = tool_response.data.get('tasks', [])
                new_context['last_listed_tasks'] = [task.get('id') for task in tasks if task.get('id')]

        elif function_name == "update_task" and tool_response.success:
            if hasattr(tool_response, 'data') and tool_response.data:
                task_data = tool_response.data.get('task') or tool_response.data
                if isinstance(task_data, dict) and 'id' in task_data:
                    new_context['last_updated_task_id'] = task_data['id']

        return new_context

    async def execute_conditional_chain(
        self,
        conditional_steps: List[Dict[str, Any]],
        token: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a chain of tool calls with conditional logic.

        Args:
            conditional_steps: List of steps with conditionals
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Dictionary with success status and results
        """
        results = []
        context = {}

        for step in conditional_steps:
            # Check condition if present
            condition = step.get("condition")
            if condition:
                condition_met = await self._evaluate_condition(condition, context)
                if not condition_met:
                    # Skip this step
                    results.append({
                        "step_skipped": True,
                        "condition": condition,
                        "evaluated_to": False
                    })
                    continue

            # Execute the tool call in the step
            tool_call = step.get("tool_call", {})
            function_name = tool_call.get("name", tool_call.get("function", {}).get("name"))
            function_args = tool_call.get("arguments", tool_call.get("function", {}).get("arguments", {}))

            # If arguments is a string, parse it as JSON
            if isinstance(function_args, str):
                import json
                try:
                    function_args = json.loads(function_args)
                except json.JSONDecodeError:
                    error_msg = f"Invalid JSON arguments for tool {function_name}"
                    return {
                        "success": False,
                        "error": error_msg,
                        "partial_results": results
                    }

            # Update arguments with context
            updated_args = self._update_args_with_context(function_args, context)

            try:
                # Execute the tool
                tool_response = await tool_registry.execute_tool(function_name, updated_args, token)

                # Store result
                result = {
                    "tool": function_name,
                    "input": updated_args,
                    "output": tool_response,
                    "success": tool_response.success,
                    "condition_applied": bool(condition)
                }
                results.append(result)

                # Update context for subsequent steps
                context = self._update_context(context, function_name, tool_response)

            except Exception as e:
                error_msg = f"Error executing conditional step: {str(e)}"
                agent_logger.error(
                    error_msg,
                    context={"step": step},
                    user_id=user_id
                )

                result = {
                    "tool": function_name,
                    "input": updated_args,
                    "output": None,
                    "success": False,
                    "error": str(e)
                }
                results.append(result)

        return {
            "success": True,
            "results": results,
            "context": context
        }

    async def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition based on context.

        Args:
            condition: Condition to evaluate
            context: Current context

        Returns:
            Boolean result of condition evaluation
        """
        condition_type = condition.get("type")
        condition_value = condition.get("value")

        if condition_type == "has_value_in_context":
            key = condition_value.get("key")
            return key in context and context[key] is not None

        elif condition_type == "context_equals":
            key = condition_value.get("key")
            expected = condition_value.get("expected")
            return key in context and context[key] == expected

        elif condition_type == "context_contains":
            key = condition_value.get("key")
            expected = condition_value.get("expected")
            if key in context and isinstance(context[key], list):
                return expected in context[key]
            return False

        # Default to True if condition type is unknown
        return True


# Global instance
tool_chain_executor = ToolChainExecutor()