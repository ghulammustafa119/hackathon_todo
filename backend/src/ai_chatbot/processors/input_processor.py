"""Processors for natural language input and response formatting."""

from typing import Dict, Any, Optional
from ..utils.nlp_utils import (
    extract_task_parameters,
    detect_intent,
    extract_task_id,
    extract_task_reference,
    normalize_task_title,
    extract_completion_status
)
from ..utils.response_formatter import (
    format_task_response,
    format_tasks_list_response,
    format_error_response,
    format_confirmation_response,
    format_clarification_request
)
from ..agents.openai_agent import chatbot_agent


class InputProcessor:
    """Processes natural language input for task management operations."""

    def __init__(self):
        # DISABLED (Phase III): Conversation memory is disabled to comply with
        # the Stateless System Rule. Deferred to Phase V.
        self.agent = chatbot_agent

    async def process_task_creation(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input for task creation.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Extract parameters from the input
        params = extract_task_parameters(text)

        # If no title was extracted, ask for clarification
        if not params.get('title'):
            return format_clarification_request(
                "I couldn't identify a task title in your request. Could you please specify what task you'd like to create?"
            )

        # Use the agent to create the task
        return await self.agent.process_request(text, token, user_id)

    async def process_task_listing(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input for task listing.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Determine if the user wants to filter tasks
        filter_param = None
        if 'pending' in text.lower() or 'incomplete' in text.lower():
            filter_param = 'pending'
        elif 'completed' in text.lower() or 'done' in text.lower():
            filter_param = 'completed'

        # Use the agent to list tasks
        return await self.agent.process_request(text, token, user_id)

    async def process_task_update(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input for task updates.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Extract task ID if explicitly mentioned
        task_id = extract_task_id(text)

        # If no task ID found, try to extract task reference
        if not task_id:
            task_ref = extract_task_reference(text)
            if task_ref:
                # In a real implementation, we'd search for the task by reference
                # For now, we'll let the agent handle this
                pass

        # Use the agent to update the task
        return await self.agent.process_request(text, token, user_id)

    async def process_task_deletion(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input for task deletion.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Extract task ID if explicitly mentioned
        task_id = extract_task_id(text)

        # If no task ID found, try to extract task reference
        if not task_id:
            task_ref = extract_task_reference(text)
            if task_ref:
                # In a real implementation, we'd search for the task by reference
                # For now, we'll let the agent handle this
                pass

        # Use the agent to delete the task
        return await self.agent.process_request(text, token, user_id)

    async def process_task_completion(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input for task completion.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Extract task ID if explicitly mentioned
        task_id = extract_task_id(text)

        # Determine completion status
        completion_status = extract_completion_status(text)
        if completion_status is None:
            # Default to True (completed) if not specified
            completion_status = True

        # If no task ID found, try to extract task reference
        if not task_id:
            task_ref = extract_task_reference(text)
            if task_ref:
                # In a real implementation, we'd search for the task by reference
                # For now, we'll let the agent handle this
                pass

        # Use the agent to complete the task
        return await self.agent.process_request(text, token, user_id)

    async def process_input(self, text: str, token: str, user_id: str) -> str:
        """
        Process natural language input and determine appropriate action.

        Args:
            text: Natural language input
            token: JWT token for authentication
            user_id: User ID for logging

        Returns:
            Natural language response
        """
        # Detect the user's intent
        intent = detect_intent(text)

        # Process based on detected intent
        if intent == 'create_task':
            return await self.process_task_creation(text, token, user_id)
        elif intent == 'list_tasks':
            return await self.process_task_listing(text, token, user_id)
        elif intent == 'update_task':
            return await self.process_task_update(text, token, user_id)
        elif intent == 'delete_task':
            return await self.process_task_deletion(text, token, user_id)
        elif intent == 'complete_task':
            return await self.process_task_completion(text, token, user_id)
        else:
            # Default to the agent's processing if intent is unclear
            return await self.agent.process_request(text, token, user_id)

    def preprocess_input(self, text: str) -> str:
        """
        Preprocess natural language input to clean and normalize.

        Args:
            text: Raw input text

        Returns:
            Preprocessed text
        """
        # Basic preprocessing
        text = text.strip()

        # Normalize common abbreviations or phrases
        replacements = {
            "w/": "with",
            "w/o": "without",
            "u": "you",
            "ur": "your",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


class ResponseFormatter:
    """Formats responses from MCP tools into natural language."""

    def __init__(self):
        pass

    def format_task_creation_response(self, task_data: Dict[str, Any]) -> str:
        """Format response for task creation."""
        if not task_data:
            return "Task created successfully."

        return format_task_response(task_data, "created")

    def format_task_list_response(self, tasks_list: list) -> str:
        """Format response for task listing."""
        return format_tasks_list_response(tasks_list)

    def format_task_update_response(self, task_data: Dict[str, Any]) -> str:
        """Format response for task update."""
        if not task_data:
            return "Task updated successfully."

        return format_task_response(task_data, "updated")

    def format_task_deletion_response(self, task_id: str) -> str:
        """Format response for task deletion."""
        return format_confirmation_response("deleted", f"task {task_id}")

    def format_task_completion_response(self, task_data: Dict[str, Any]) -> str:
        """Format response for task completion."""
        if not task_data:
            return "Task completion status updated successfully."

        return format_task_response(task_data, "completed")

    def format_error_response(self, error_code: str, error_message: str) -> str:
        """Format error response."""
        return format_error_response(error_code, error_message)

    def format_generic_response(self, message: str) -> str:
        """Format a generic response."""
        return message


# Global instances
input_processor = InputProcessor()
response_formatter = ResponseFormatter()