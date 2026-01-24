"""OpenAI Agent for handling natural language task management."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from ..config import config
from ..tools.registration import tool_registry
from ..utils.response_formatter import (
    format_task_response,
    format_tasks_list_response,
    format_error_response,
    format_confirmation_response
)
from ..utils.logging import agent_logger, log_agent_operation


class OpenAIChatbotAgent:
    """AI Agent that processes natural language and maps to MCP tools."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model
        self.timeout = config.agent_timeout

        # Define the tools that the agent can use
        self.tools = self._get_available_tools()

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of available MCP tools for the agent.

        Returns:
            List of tool definitions in OpenAI-compatible format
        """
        tools = []

        # Define create_task tool
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

        # Define list_tasks tool
        # DISABLED (Phase III): Filtering is disabled to comply with the Stateless System Rule. Deferred to Phase V.
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

        # Define update_task tool
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

        # Define delete_task tool
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

        # Define complete_task tool
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

        return tools

    async def process_request(
        self,
        user_input: str,
        token: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Process a natural language request from the user.

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
            # Create a chat completion with the tools
            # Each request is stateless and independent
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant that helps users manage their tasks. "
                            "Use the provided tools to create, read, update, delete, and manage tasks. "
                            "Always ensure the user is authenticated and authorized to perform operations. "
                            "If the user's request is ambiguous, ask for clarification. "
                            "Always respect user boundaries and only allow operations on the user's own tasks."
                            "DO NOT maintain any conversation memory or context between requests."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                tools=self.tools,
                tool_choice="auto",
                timeout=self.timeout
            )

            # Process the response
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Execute the requested tools
                final_response = await self._execute_tool_calls(tool_calls, token, user_input)
            else:
                # No tool calls needed, return the assistant's message
                final_response = response_message.content or "I processed your request."

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

    async def _execute_tool_calls(
        self,
        tool_calls: List,
        token: str,
        original_input: str
    ) -> str:
        """
        Execute the requested tool calls and format the response.

        Args:
            tool_calls: List of tool calls to execute
            token: JWT token for authentication
            original_input: Original user input for context

        Returns:
            Formatted response for the user
        """
        responses = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            try:
                # Execute the tool
                tool_response = await tool_registry.execute_tool(function_name, function_args, token)

                if tool_response.success:
                    # Format the successful response
                    if function_name == "create_task":
                        response_text = format_task_response(tool_response.data.get('task', {}), "created")
                    elif function_name == "list_tasks":
                        tasks = tool_response.data.get('tasks', [])
                        response_text = format_tasks_list_response(tasks)
                    elif function_name == "update_task":
                        response_text = format_task_response(tool_response.data.get('task', {}), "updated")
                    elif function_name == "delete_task":
                        response_text = format_confirmation_response("deleted", "task")
                    elif function_name == "complete_task":
                        response_text = format_task_response(tool_response.data.get('task', {}), "completed")
                    else:
                        response_text = f"Operation completed: {function_name}"

                    responses.append(response_text)
                else:
                    # Format the error response
                    error_code = tool_response.error.get('code', 'UNKNOWN_ERROR') if tool_response.error else 'UNKNOWN_ERROR'
                    error_msg = tool_response.error.get('message', 'Unknown error occurred') if tool_response.error else 'Unknown error occurred'

                    error_response = format_error_response(error_code, error_msg)
                    responses.append(error_response)

            except Exception as e:
                # Handle tool execution errors
                error_response = format_error_response(
                    "TOOL_EXECUTION_ERROR",
                    f"Failed to execute {function_name}: {str(e)}"
                )
                responses.append(error_response)

        # Combine all responses
        if len(responses) == 1:
            return responses[0]
        else:
            return " ".join(responses)

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
chatbot_agent = OpenAIChatbotAgent()