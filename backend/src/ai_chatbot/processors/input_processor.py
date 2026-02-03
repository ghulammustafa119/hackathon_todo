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
from ..agents.cohere_agent import chatbot_agent
from ..tools import loader  # Import to ensure all tools are loaded and registered


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
        try:
            from ..services.task_index_mapper import task_index_mapper
            from ...database.session import get_session
            from ...models.task import Task
            from sqlmodel import select

            # Use the agent to list tasks
            result = await self.agent.process_request(text, token, user_id)

            # Get tasks directly from the database to store the index mapping
            # This avoids potential issues with HTTP calls within the same process
            with next(get_session()) as session:
                statement = select(Task).where(Task.user_id == str(user_id))
                tasks_from_db = session.exec(statement).all()

                # Convert tasks to the expected format
                user_tasks = []
                for task in tasks_from_db:
                    task_dict = {
                        'id': str(task.id),
                        'title': task.title,
                        'description': task.description,
                        'completed': task.completed,
                        'created_at': task.created_at.isoformat() if task.created_at else None,
                        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                        'user_id': str(task.user_id)
                    }
                    user_tasks.append(task_dict)

            # Store the task list for future reference
            task_index_mapper.store_task_list(user_id, user_tasks)

            # Log the number of tasks stored for debugging
            from ..utils.logging import agent_logger
            agent_logger.info(f"Stored {len(user_tasks)} tasks for user {user_id} in task index mapper")
        except Exception as e:
            # If storing the task list fails, log the error for debugging
            from ..utils.logging import agent_logger
            agent_logger.error(f"Failed to store task list for user {user_id}: {str(e)}")
            # If storing the task list fails, it's not critical, just continue with the original result
            pass

        return result

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

        # Check if user is referring to a numbered task (like "task 3" from the list)
        import re
        number_match = re.search(r'(?:task|number|#)\s*(\d+)', text, re.IGNORECASE)

        if number_match:
            # User is referring to a numbered task from the last list
            task_number = int(number_match.group(1))

            # Import the task index mapper to use conversation memory
            from ..services.task_index_mapper import task_index_mapper

            # Check if we have a recent task list for this user
            if task_index_mapper.has_recent_task_list(user_id):
                # Use the stored mapping to get the actual task ID
                actual_task_id = task_index_mapper.get_task_id_by_index(user_id, task_number)

                if actual_task_id:
                    # Validate that the task_id is a proper UUID
                    from ..utils.validation import validate_task_id
                    if validate_task_id(actual_task_id):
                        # Modify the original request to include the proper task ID
                        modified_request = f'delete_task with task_id "{actual_task_id}"'
                        return await self.agent.process_request(modified_request, token, user_id)
                    else:
                        from ..utils.response_formatter import format_error_response
                        return format_error_response("INVALID_TASK_ID", f"The task ID for task #{task_number} is invalid.")
                else:
                    from ..utils.response_formatter import format_error_response
                    # Get current task list to see if the number is out of range
                    from ..services.api_client import backend_client
                    try:
                        response = await backend_client.list_tasks(token=token)
                        user_tasks = response.get('tasks', []) if isinstance(response, dict) else []
                        return format_error_response("TASK_NOT_FOUND", f"You don't have a task #{task_number}. You have {len(user_tasks)} tasks total.")
                    except Exception:
                        return format_error_response("TASK_NOT_FOUND", f"Could not find task #{task_number}. The task list may have changed since you last viewed it.")
            else:
                # No recent task list, so we need to fetch it to map the index
                from ..services.api_client import backend_client
                try:
                    response = await backend_client.list_tasks(token=token)
                    user_tasks = response.get('tasks', []) if isinstance(response, dict) else []

                    if task_number > 0 and task_number <= len(user_tasks):
                        # Valid task number - get the actual task ID
                        target_task = user_tasks[task_number - 1]  # 0-indexed
                        actual_task_id = target_task.get('id')

                        # Validate that the task_id is a proper UUID
                        from ..utils.validation import validate_task_id
                        if actual_task_id and validate_task_id(actual_task_id):
                            # Store the task list for future reference
                            from ..services.task_index_mapper import task_index_mapper
                            task_index_mapper.store_task_list(user_id, user_tasks)

                            # Modify the original request to include the proper task ID
                            modified_request = f'delete_task with task_id "{actual_task_id}"'
                            return await self.agent.process_request(modified_request, token, user_id)
                        else:
                            from ..utils.response_formatter import format_error_response
                            return format_error_response("INVALID_TASK_ID", f"The task ID for task #{task_number} is invalid.")
                    else:
                        from ..utils.response_formatter import format_error_response
                        return format_error_response("TASK_NOT_FOUND", f"You don't have a task #{task_number}. You have {len(user_tasks)} tasks total.")
                except Exception as e:
                    from ..utils.response_formatter import format_error_response
                    return format_error_response("FETCH_TASKS_ERROR", f"Could not fetch your tasks to find task #{task_number}. Error: {str(e)}")

        # If no numbered reference, proceed with title-based search
        # Extract task ID if explicitly mentioned
        task_id = extract_task_id(text)

        if not task_id:
            task_ref = extract_task_reference(text)
            if not task_ref:
                # If no reference found, try to extract a potential title from the text
                # Look for patterns like "delete 'task title'" or "remove 'task title'"
                match = re.search(r'(delete|remove|erase|cancel)\s+(.+?)(?:\s+task|\s+item|$)', text, re.IGNORECASE)
                if match:
                    task_ref = match.group(2).strip()

            # Original behavior - search by title
            # Import task resolver to find the task by title
            from ..utils.task_resolver import resolve_tasks_by_title, format_task_list_for_user

            # Find matching tasks by title only if task_ref is not None
            if task_ref:
                matching_tasks = await resolve_tasks_by_title(task_ref, token, user_id)
            else:
                matching_tasks = []

            if len(matching_tasks) == 0:
                # No matching tasks found - show user their tasks and ask for clarification
                try:
                    # Get tasks directly from the database to avoid HTTP call issues
                    from ...database.session import get_session
                    from ...models.task import Task
                    from sqlmodel import select

                    with next(get_session()) as session:
                        statement = select(Task).where(Task.user_id == str(user_id))
                        tasks_from_db = session.exec(statement).all()

                        # Convert tasks to the expected format
                        user_tasks = []
                        for task in tasks_from_db:
                            task_dict = {
                                'id': str(task.id),
                                'title': task.title,
                                'description': task.description,
                                'completed': task.completed,
                                'created_at': task.created_at.isoformat() if task.created_at else None,
                                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                                'user_id': str(task.user_id)
                            }
                            user_tasks.append(task_dict)

                    # Store the task list for future reference
                    from ..services.task_index_mapper import task_index_mapper
                    task_index_mapper.store_task_list(user_id, user_tasks)

                    # Log the number of tasks stored for debugging
                    from ..utils.logging import agent_logger
                    agent_logger.info(f"Stored {len(user_tasks)} tasks for user {user_id} in task index mapper for deletion flow")

                    if not user_tasks:
                        return "I couldn't find a task with title containing '{}' and you don't have any tasks yet. Would you like to create a new task?".format(task_ref)
                    else:
                        from ..utils.task_resolver import format_task_list_for_user
                        available_tasks_str = format_task_list_for_user(user_tasks)
                        from ..utils.response_formatter import format_clarification_request
                        return format_clarification_request(
                            f"I couldn't find a task with title containing '{task_ref}'. Here are your current tasks:\n{available_tasks_str}\n\nWhich task would you like to delete?"
                        )
                except Exception:
                    from ..utils.response_formatter import format_error_response
                    return format_error_response("FETCH_TASKS_ERROR", f"I couldn't find a task with title containing '{task_ref}'. Could you please specify another task or check the spelling?")
            elif len(matching_tasks) == 1:
                # Exactly one match - proceed with deletion
                matched_task = matching_tasks[0]
                task_id = matched_task.get('id')

                # Validate that the task_id is a proper UUID
                from ..utils.validation import validate_task_id
                if task_id and not validate_task_id(task_id):
                    from ..utils.response_formatter import format_error_response
                    return format_error_response("INVALID_TASK_ID", f"Found a task but its ID is invalid: {task_id}")

                # Modify the original request to include the proper task ID
                # We need to create a new request that the agent can process
                modified_request = f'delete_task with task_id "{task_id}"'
                return await self.agent.process_request(modified_request, token, user_id)
            else:
                # Multiple matches - ask user to clarify
                from ..utils.response_formatter import format_clarification_request
                task_list_str = format_task_list_for_user(matching_tasks)
                return format_clarification_request(f"Multiple tasks match '{task_ref}'. {task_list_str}")

        # If we have a valid task ID, proceed with the original flow
        if task_id:
            # Validate that the task_id is a proper UUID
            from ..utils.validation import validate_task_id
            if not validate_task_id(task_id):
                from ..utils.response_formatter import format_error_response
                return format_error_response("INVALID_TASK_ID", f"The task ID '{task_id}' is not valid.")

            # Use the agent to delete the task
            return await self.agent.process_request(text, token, user_id)

        # If no task ID or reference found, let the agent handle it
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

        # If no task ID found, try to extract task reference by title
        if not task_id:
            task_ref = extract_task_reference(text)
            if not task_ref:
                # If no reference found, try to extract a potential title from the text
                # Look for patterns like "mark 'task title' as done" or "complete 'task title'"
                import re
                # Match phrases like "mark buy a pen as done" where "buy a pen" is the title
                match = re.search(r'(mark|complete|finish|done|check)\s+(.+?)(?:\s+(as\s+)?done|as\s+complete|ticked?|checked?)', text, re.IGNORECASE)
                if match:
                    task_ref = match.group(2).strip()
                    # Remove common words that might be part of the title
                    task_ref = re.sub(r'\s+(task|item)$', '', task_ref, flags=re.IGNORECASE).strip()

            # Check if the user is referring to a numbered task (like "task 3" from the list)
            import re
            number_match = re.search(r'(?:task|number|#)\s*(\d+)', text, re.IGNORECASE)

            if number_match:
                # User is referring to a numbered task from the last list
                task_number = int(number_match.group(1))

                # Import the task index mapper to use conversation memory
                from ..services.task_index_mapper import task_index_mapper

                # Check if we have a recent task list for this user
                if task_index_mapper.has_recent_task_list(user_id):
                    # Use the stored mapping to get the actual task ID
                    actual_task_id = task_index_mapper.get_task_id_by_index(user_id, task_number)

                    if actual_task_id:
                        # Validate that the task_id is a proper UUID
                        from ..utils.validation import validate_task_id
                        if validate_task_id(actual_task_id):
                            # Create a request specifically for the complete_task tool
                            modified_request = f'Complete task with ID "{actual_task_id}" and status "{completion_status}"'
                            return await self.agent.process_request(modified_request, token, user_id)
                        else:
                            from ..utils.response_formatter import format_error_response
                            return format_error_response("INVALID_TASK_ID", f"The task ID for task #{task_number} is invalid.")
                    else:
                        from ..utils.response_formatter import format_error_response
                        # Get current task list to see if the number is out of range
                        from ..services.api_client import backend_client
                        try:
                            response = await backend_client.list_tasks(token=token)
                            user_tasks = response.get('tasks', []) if isinstance(response, dict) else []
                            return format_error_response("TASK_NOT_FOUND", f"You don't have a task #{task_number}. You have {len(user_tasks)} tasks total.")
                        except Exception:
                            return format_error_response("TASK_NOT_FOUND", f"Could not find task #{task_number}. The task list may have changed since you last viewed it.")
                else:
                    # No recent task list, so we need to fetch it to map the index
                    try:
                        # Get tasks directly from the database to avoid HTTP call issues
                        from ...database.session import get_session
                        from ...models.task import Task
                        from sqlmodel import select

                        with next(get_session()) as session:
                            statement = select(Task).where(Task.user_id == str(user_id))
                            tasks_from_db = session.exec(statement).all()

                            # Convert tasks to the expected format
                            user_tasks = []
                            for task in tasks_from_db:
                                task_dict = {
                                    'id': str(task.id),
                                    'title': task.title,
                                    'description': task.description,
                                    'completed': task.completed,
                                    'created_at': task.created_at.isoformat() if task.created_at else None,
                                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                                    'user_id': str(task.user_id)
                                }
                                user_tasks.append(task_dict)

                        if task_number > 0 and task_number <= len(user_tasks):
                            # Valid task number - get the actual task ID
                            target_task = user_tasks[task_number - 1]  # 0-indexed
                            actual_task_id = target_task.get('id')

                            # Validate that the task_id is a proper UUID
                            from ..utils.validation import validate_task_id
                            if actual_task_id and validate_task_id(actual_task_id):
                                # Store the task list for future reference
                                task_index_mapper.store_task_list(user_id, user_tasks)

                                # Create a request specifically for the complete_task tool
                                modified_request = f'Complete task with ID "{actual_task_id}" and status "{completion_status}"'
                                return await self.agent.process_request(modified_request, token, user_id)
                            else:
                                from ..utils.response_formatter import format_error_response
                                return format_error_response("INVALID_TASK_ID", f"The task ID for task #{task_number} is invalid.")
                        else:
                            from ..utils.response_formatter import format_error_response
                            return format_error_response("TASK_NOT_FOUND", f"You don't have a task #{task_number}. You have {len(user_tasks)} tasks total.")
                    except Exception as e:
                        from ..utils.response_formatter import format_error_response
                        return format_error_response("FETCH_TASKS_ERROR", f"Could not fetch your tasks to find task #{task_number}. Error: {str(e)}")
            else:
                # Original behavior - search by title
                # Import task resolver to find the task by title
                from ..utils.task_resolver import resolve_tasks_by_title, format_task_list_for_user

                # Find matching tasks by title only if task_ref is not None
                if task_ref:
                    matching_tasks = await resolve_tasks_by_title(task_ref, token, user_id)
                else:
                    matching_tasks = []

                if len(matching_tasks) == 0:
                    # No matching tasks found - show user their tasks and ask for clarification
                    try:
                        # Get all user tasks to show them what's available
                        # Get tasks directly from the database to avoid HTTP call issues
                        from ...database.session import get_session
                        from ...models.task import Task
                        from sqlmodel import select

                        with next(get_session()) as session:
                            statement = select(Task).where(Task.user_id == str(user_id))
                            tasks_from_db = session.exec(statement).all()

                            # Convert tasks to the expected format
                            user_tasks = []
                            for task in tasks_from_db:
                                task_dict = {
                                    'id': str(task.id),
                                    'title': task.title,
                                    'description': task.description,
                                    'completed': task.completed,
                                    'created_at': task.created_at.isoformat() if task.created_at else None,
                                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                                    'user_id': str(task.user_id)
                                }
                                user_tasks.append(task_dict)

                        # Store the task list for future reference
                        from ..services.task_index_mapper import task_index_mapper
                        task_index_mapper.store_task_list(user_id, user_tasks)

                        # Log the number of tasks stored for debugging
                        from ..utils.logging import agent_logger
                        agent_logger.info(f"Stored {len(user_tasks)} tasks for user {user_id} in task index mapper for completion flow")

                        if not user_tasks:
                            return "I couldn't find a task with title containing '{}' and you don't have any tasks yet. Would you like to create a new task?".format(task_ref)
                        else:
                            from ..utils.task_resolver import format_task_list_for_user
                            available_tasks_str = format_task_list_for_user(user_tasks)
                            from ..utils.response_formatter import format_clarification_request
                            return format_clarification_request(
                                f"I couldn't find a task with title containing '{task_ref}'. Here are your current tasks:\n{available_tasks_str}\n\nWhich task would you like to mark as done?"
                            )
                    except Exception:
                        from ..utils.response_formatter import format_error_response
                        return format_error_response("FETCH_TASKS_ERROR", f"I couldn't find a task with title containing '{task_ref}'. Could you please specify another task or check the spelling?")
                elif len(matching_tasks) == 1:
                    # Exactly one match - proceed with completion
                    matched_task = matching_tasks[0]
                    task_id = matched_task.get('id')

                    # Validate that the task_id is a proper UUID
                    from ..utils.validation import validate_task_id
                    if task_id and not validate_task_id(task_id):
                        from ..utils.response_formatter import format_error_response
                        return format_error_response("INVALID_TASK_ID", f"Found a task but its ID is invalid: {task_id}")

                    # Create a request specifically for the complete_task tool
                    modified_request = f'Complete task with ID "{task_id}" and status "{completion_status}"'
                    return await self.agent.process_request(modified_request, token, user_id)
                else:
                    # Multiple matches - ask user to clarify
                    from ..utils.response_formatter import format_clarification_request
                    task_list_str = format_task_list_for_user(matching_tasks)
                    return format_clarification_request(f"Multiple tasks match '{task_ref}'. {task_list_str}")

        # If we have a valid task ID, proceed with the original flow
        if task_id:
            # Validate that the task_id is a proper UUID
            from ..utils.validation import validate_task_id
            if not validate_task_id(task_id):
                from ..utils.response_formatter import format_error_response
                return format_error_response("INVALID_TASK_ID", f"The task ID '{task_id}' is not valid.")

            # Create a request specifically for the complete_task tool
            modified_request = f'Complete task with ID "{task_id}" and status "{completion_status}"'
            return await self.agent.process_request(modified_request, token, user_id)

        # If no task ID or reference found, let the agent handle it
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

        # For create_task intent, we should always try to create, not search
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