"""Cohere Agent for handling natural language task management."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

from ..config import config
from ..tools.registration import tool_registry
from ..utils.response_formatter import (
    format_task_response,
    format_tasks_list_response,
    format_error_response,
    format_confirmation_response
)
from ..utils.logging import agent_logger, log_agent_operation
from ...services.cohere_client import get_cohere_response
from ..tools import loader  # Import to ensure all tools are loaded and registered
from ..services.task_index_mapper import task_index_mapper


class CohereChatbotAgent:
    """AI Agent that processes natural language and maps to MCP tools using Cohere API."""

    def __init__(self):
        # No initialization needed as Cohere client is managed by the service
        from ..config import config
        self.model = config.cohere_model

        # Define the tools that the agent can use
        self.tools = self._get_available_tools()

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of available MCP tools for the agent.

        Returns:
            List of tool definitions in JSON format for function calling simulation
        """
        tools = []

        # Define create_task tool
        tools.append({
            "name": "create_task",
            "description": "Create a new task with title, description, and optional due date",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the task to be created"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in ISO 8601 format (YYYY-MM-DD)"
                    }
                },
                "required": ["title"]
            }
        })

        # Define list_tasks tool
        # DISABLED (Phase III): Filtering is disabled to comply with the Stateless System Rule. Deferred to Phase V.
        tools.append({
            "name": "list_tasks",
            "description": "Retrieve tasks (filtering disabled in Phase III)",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by completion status - IGNORED in Phase III"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return - IGNORED in Phase III"
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Optional search term to filter tasks by title or description - IGNORED in Phase III"
                    }
                }
            }
        })

        # Define update_task tool
        tools.append({
            "name": "update_task",
            "description": "Update an existing task with new values",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO 8601 format (optional)"
                    }
                },
                "required": ["task_id"]
            }
        })

        # Define delete_task tool
        tools.append({
            "name": "delete_task",
            "description": "Delete an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        })

        # Define complete_task tool
        tools.append({
            "name": "complete_task",
            "description": "Toggle the completion status of a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to update completion status"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Desired completion status (true for completed, false for incomplete)"
                    }
                },
                "required": ["task_id", "completed"]
            }
        })

        return tools

    async def _resolve_task_id(self, arguments: Dict[str, Any], user_id: Optional[str], tool_name: str) -> Optional[str]:
        """
        Resolve task_id from various sources:
        1. Direct task_id in arguments
        2. Numeric index (e.g., "3" -> actual task id)
        3. Most recently referenced task

        Args:
            arguments: Tool arguments containing potential task_id
            user_id: User ID for lookup
            tool_name: Name of the tool requesting resolution

        Returns:
            Resolved task_id or None if not found
        """
        task_id = arguments.get("task_id")

        if not task_id:
            # No task_id provided, try to get most recent task
            recent_task_id = task_index_mapper.get_most_recent_task_id(user_id)
            return recent_task_id

        # Check if task_id is a number (user is referring to task by index)
        import re
        number_match = re.match(r'^(\d+)$', str(task_id))
        if number_match:
            task_number = int(number_match.group(1))

            # Try to resolve the index to actual task_id using our mapper
            actual_task_id = None
            if user_id:
                actual_task_id = task_index_mapper.get_task_id_by_index(user_id, task_number)

            return actual_task_id

        # If it's not a number, return as-is (assuming it's a real task_id)
        return str(task_id)

    async def _handle_tool_execution_and_format_response(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        token: str,
        user_id: Optional[str]
    ) -> str:
        """
        Handle task ID resolution and execute tool, then format the response appropriately.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Formatted response string
        """
        # For certain tools, resolve the task_id properly
        if tool_name in ["update_task", "delete_task", "complete_task"]:
            resolved_task_id = await self._resolve_task_id(arguments, user_id, tool_name)

            if not resolved_task_id:
                # Check if we have recent tasks but the index is out of range
                if user_id and task_index_mapper.has_recent_task_list(user_id):
                    # Get the last task list to check if the index is out of range
                    last_tasks = task_index_mapper.get_last_task_list(user_id)
                    if last_tasks:
                        resolution_error = {
                            "code": "TASK_INDEX_OUT_OF_RANGE",
                            "message": f"You don't have a task #{arguments.get('task_id', '?')}. You have {len(last_tasks)} tasks total."
                        }
                    else:
                        resolution_error = {
                            "code": "TASK_NOT_FOUND",
                            "message": f"Could not find task #{arguments.get('task_id', '?')}. Please say 'show my tasks' first to see your current tasks."
                        }
                else:
                    resolution_error = {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Could not find task #{arguments.get('task_id', '?')}. Please say 'show my tasks' first to see your current tasks."
                    }

                class ErrorResponse:
                    success = False
                    data = {}
                    error = resolution_error

                tool_response = ErrorResponse()
            else:
                # Update the arguments with the resolved task_id
                arguments["task_id"] = resolved_task_id
                # Execute the identified tool - pass user_id instead of token for authentication
                tool_response = await self._execute_single_tool(tool_name, arguments, token, user_id)
        else:
            # Execute the identified tool - pass user_id instead of token for authentication
            tool_response = await self._execute_single_tool(tool_name, arguments, token, user_id)

        if tool_response.success:
            # Format the successful response based on the tool
            if tool_name == "create_task":
                task_data = tool_response.data.get('task', {})
                if task_data:
                    response_text = format_task_response(task_data, "created")
                    # Store the newly created task as most recent
                    if user_id and 'id' in task_data:
                        task_index_mapper.set_most_recent_task_id(user_id, task_data['id'])
                else:
                    response_text = "Task created successfully!"
            elif tool_name == "list_tasks":
                tasks = tool_response.data.get('tasks', [])
                response_text = format_tasks_list_response(tasks)

                # Store the task list for future reference
                if user_id:
                    task_index_mapper.store_task_list(user_id, tasks)
            elif tool_name == "update_task":
                task_data = tool_response.data.get('task', {})
                if task_data:
                    response_text = format_task_response(task_data, "updated")
                else:
                    response_text = "Task updated successfully!"
            elif tool_name == "delete_task":
                response_text = format_confirmation_response("deleted", "task")
            elif tool_name == "complete_task":
                task_data = tool_response.data.get('task', {})
                if task_data:
                    response_text = format_task_response(task_data, "completed")
                else:
                    response_text = "Task completion status updated successfully!"
            else:
                response_text = f"Operation completed: {tool_name}"
        else:
            # Format the error response
            error_code = tool_response.error.get('code', 'UNKNOWN_ERROR') if tool_response.error else 'UNKNOWN_ERROR'
            error_msg = tool_response.error.get('message', 'Unknown error occurred') if tool_response.error else 'Unknown error occurred'
            response_text = format_error_response(error_code, error_msg)
            agent_logger.error(f"Tool execution failed: {error_code} - {error_msg}")

        return response_text

    async def process_request(
        self,
        user_input: str,
        token: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Process a natural language request from the user using Cohere API.

        DISABLED (Phase III): Conversation memory is disabled to comply with
        the Stateless System Rule. Deferred to Phase V.

        Args:
            user_input: Natural language input from the user
            token: JWT token for authentication
            user_id: User ID for logging (optional)

        Returns:
            Natural language response for the user
        """
        start_time = __import__('time').time()

        try:
            # Prepare the system prompt for the Cohere model
            system_prompt = (
                "You are an AI assistant that helps users manage their tasks using predefined tools. "
                "Available tools: create_task, list_tasks, update_task, delete_task, complete_task. "
                "NEVER invent or use any other tool names besides these exact ones. "
                "Understand the user's request and respond with ONLY JSON that indicates which of these EXACT tools to call and with what parameters. "
                "If the user wants to create a task, use 'create_task' regardless of how they phrase their request (e.g., 'add', 'create', 'make', 'buy', 'get', 'for me', 'need to', 'want to'). "
                "For creation requests like 'buy a car for me', 'need to schedule meeting', 'want to add groceries', always use 'create_task'. "
                "For listing requests like 'show my tasks', 'what are my tasks', 'list tasks', 'see tasks', 'view tasks', always use 'list_tasks' with empty arguments: {\"tool\": \"list_tasks\", \"arguments\": {}}. "
                "For updating tasks, always include the 'task_id' parameter. "
                "For deleting tasks, always include the 'task_id' parameter. "
                "For completing tasks, always include the 'task_id' and 'completed' (true/false) parameters. "
                "When user refers to numbered tasks (e.g., 'delete task 3', 'mark task 5 as done'), they are referring to the task number from the last list_tasks result. "
                "You must pass the task NUMBER as the task_id parameter, and the system will resolve it to the actual task ID. "
                "For example, if user says 'Delete task 3', call delete_task with task_id: 3, and the system will resolve index 3 to the actual task ID. "
                "Always ensure the user is authenticated and authorized to perform operations. "
                "If the user's request is ambiguous, ask for clarification EXCEPT for commands like 'mark it', 'delete it', 'complete it', which must never trigger clarification."
                "For commands like 'mark it' or 'complete it', ALWAYS call complete_task with completed=true using the MOST RECENT task number."
                "NEVER attempt to identify or resolve tasks by title, text matching, or semantic similarity. Task identification MUST be numeric only."
                "After calling list_tasks, the returned list is the ONLY valid source for task numbering until another list_tasks call occurs."
                "Always respect user boundaries and only allow operations on the user's own tasks. "
                "DO NOT maintain any conversation memory or context between requests. "
                "RESPOND WITH VALID JSON ONLY - NO EXTRA TEXT, NO MARKDOWN, NO EXPLANATIONS. "
                "Return ONLY JSON in the format: {\"tool\": \"EXACT_TOOL_NAME_FROM_LIST\", \"arguments\": {...}} "
                "Example: If user says 'Add a task to buy a pen', respond with ONLY: {\"tool\": \"create_task\", \"arguments\": {\"title\": \"buy a pen\"}}\n"
                "Example: If user says 'Buy a car for me', respond with ONLY: {\"tool\": \"create_task\", \"arguments\": {\"title\": \"buy a car\"}}\n"
                "Example: If user says 'Show my tasks', respond with ONLY: {\"tool\": \"list_tasks\", \"arguments\": {}}"
                "Example: If user says 'Delete task 3' (after seeing a list), respond with ONLY: {\"tool\": \"delete_task\", \"arguments\": {\"task_id\": 3}} (the system will resolve index 3 to the actual task ID)"
            )

            # Combine the system prompt and user input for Cohere
            combined_prompt = f"{system_prompt}\n\nUser request: {user_input}"

            # Call the Cohere service to get the response
            cohere_response = get_cohere_response(combined_prompt, system_prompt)

            # Try to parse the response as JSON to see if it contains tool calls
            try:
                # Look for JSON-like structure in the response
                import re
                json_match = re.search(r'\{.*\}', cohere_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()

                    # Parse as strict JSON
                    parsed_response = json.loads(json_str)

                    # Check if it contains tool information
                    if parsed_response and "tool" in parsed_response:
                        tool_name = parsed_response["tool"]
                        arguments = parsed_response.get("arguments", {})

                        # Log the detected tool for debugging
                        agent_logger.info(f"Detected tool call: {tool_name} with args: {arguments}")

                        # Validate that the tool name is one of the allowed tools
                        allowed_tools = {"create_task", "list_tasks", "update_task", "delete_task", "complete_task"}
                        if tool_name not in allowed_tools:
                            agent_logger.warning(f"Invalid tool name detected: {tool_name}")
                            final_response = f"Sorry, I cannot perform the requested action. Available tools are: {', '.join(allowed_tools)}"
                        else:
                            # Handle all tools through the common handler
                            final_response = await self._handle_tool_execution_and_format_response(
                                tool_name, arguments, token, user_id
                            )
                    else:
                        # If no tool call was identified, return the generated text as is
                        final_response = cohere_response
                        agent_logger.debug(f"No tool detected in response, returning as-is: {cohere_response[:200]}...")
                else:
                    # If no JSON found, return the generated text as is
                    final_response = cohere_response
                    agent_logger.debug(f"No JSON found in response, returning as-is: {cohere_response[:200]}...")

            except json.JSONDecodeError as e:
                # If JSON parsing fails, return an error
                agent_logger.warning(f"JSON decode error in Cohere response: {str(e)}, response: {cohere_response[:200]}...")
                final_response = "I encountered an error processing your request. Please try rephrasing."
            except Exception as e:
                # If any other error occurs during processing, return an error
                agent_logger.warning(f"Error processing Cohere response: {str(e)}")
                final_response = "I encountered an error processing your request. Please try rephrasing."

            # Log the operation
            duration = (__import__('time').time() - start_time) * 1000
            log_agent_operation(
                operation="process_request",
                user_id=user_id or "unknown",
                success=True,
                duration_ms=duration,
                details={"input_length": len(user_input)}
            )

            return final_response

        except Exception as e:
            # Log the error
            duration = (__import__('time').time() - start_time) * 1000
            log_agent_operation(
                operation="process_request",
                user_id=user_id or "unknown",
                success=False,
                duration_ms=duration,
                details={"error": str(e), "input_length": len(user_input)}
            )

            agent_logger.error(
                f"Error processing request: {str(e)}",
                context={"input": user_input[:100]},  # Limit context size
                user_id=user_id
            )

            return f"I encountered an error while processing your request: {str(e)}"

    async def _execute_single_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        token: str,
        user_id: Optional[str] = None
    ) -> Any:
        """
        Execute a single tool call.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            token: JWT token for authentication (kept for backward compatibility but not used)
            user_id: User ID for authentication (validated at API level)

        Returns:
            Result of the tool execution
        """
        try:
            # Execute the tool - Note: execute_tool is now async
            tool_response = await tool_registry.execute_tool(tool_name, arguments, token, user_id)
            return tool_response
        except Exception as e:
            # Create an error response
            class ErrorResponse:
                success = False
                data = {}
                error = {"code": "TOOL_EXECUTION_ERROR", "message": str(e)}

            return ErrorResponse()

    def get_available_tools(self) -> Dict[str, str]:
        """
        Get a list of available tools with descriptions.

        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            "create_task": "Create a new task with title, description, and optional due date",
            "list_tasks": "Retrieve tasks (filtering disabled in Phase III)",  # DISABLED (Phase III): Filtering is disabled to comply with the Stateless System Rule. Deferred to Phase V.
            "update_task": "Update an existing task with new values",
            "delete_task": "Delete an existing task",
            "complete_task": "Toggle the completion status of a task"
        }


# Global agent instance
chatbot_agent = CohereChatbotAgent()
