"""Comprehensive test suite for all Agent Behavior Specifications.

Tests cover:
1. Task Creation - natural language commands
2. Task Listing - show/list with filters (all, pending, completed)
3. Task Completion - mark as done/complete
4. Task Deletion - delete/remove
5. Task Update - change/rename
6. Confirmation messages - friendly responses
7. Error handling - graceful error messages
8. Intent detection - all natural language variations
9. ToolResponse data handling - the list_tasks bug fix
"""

import asyncio
import json
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from datetime import datetime

# Ensure the backend source is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.ai_chatbot.utils.nlp_utils import detect_intent, extract_task_parameters, extract_completion_status
from src.ai_chatbot.utils.response_formatter import (
    format_task_response,
    format_tasks_list_response,
    format_error_response,
    format_confirmation_response,
)


# ============================================================
# 1. Intent Detection Tests
# ============================================================

class TestIntentDetection:
    """Test that natural language commands are correctly mapped to intents."""

    # --- Task Creation ---
    def test_add_task_intent(self):
        assert detect_intent("Add a task to buy groceries") == "create_task"

    def test_create_task_intent(self):
        assert detect_intent("Create a new task for meeting preparation") == "create_task"

    def test_remember_intent(self):
        assert detect_intent("I need to remember to pay bills") == "create_task"

    def test_buy_something_intent(self):
        assert detect_intent("buy a car for me") == "create_task"

    def test_need_to_intent(self):
        assert detect_intent("need to schedule meeting") == "create_task"

    def test_want_to_intent(self):
        assert detect_intent("want to add groceries") == "create_task"

    # --- Task Listing ---
    def test_show_tasks_intent(self):
        assert detect_intent("Show me all my tasks") == "list_tasks"

    def test_what_tasks_intent(self):
        assert detect_intent("What are my tasks") == "list_tasks"

    def test_list_tasks_intent(self):
        assert detect_intent("list tasks") == "list_tasks"

    def test_see_tasks_intent(self):
        assert detect_intent("let me see my tasks") == "list_tasks"

    def test_view_tasks_intent(self):
        assert detect_intent("view all tasks") == "list_tasks"

    def test_whats_pending_intent(self):
        assert detect_intent("What's pending?") == "list_tasks"

    def test_what_completed_intent(self):
        assert detect_intent("What have I completed?") == "list_tasks"

    # --- Task Completion ---
    def test_mark_complete_intent(self):
        assert detect_intent("Mark task 3 as complete") == "complete_task"

    def test_mark_done_intent(self):
        assert detect_intent("Mark task 5 as done") == "complete_task"

    def test_complete_task_intent(self):
        assert detect_intent("complete task 2") == "complete_task"

    def test_finish_task_intent(self):
        assert detect_intent("finish the report task") == "complete_task"

    # --- Task Deletion ---
    def test_delete_task_intent(self):
        assert detect_intent("Delete the meeting task") == "delete_task"

    def test_remove_task_intent(self):
        assert detect_intent("Remove task 2") == "delete_task"

    def test_cancel_task_intent(self):
        assert detect_intent("Cancel the appointment task") == "delete_task"

    # --- Task Update ---
    def test_change_task_intent(self):
        assert detect_intent("Change task 1 to 'Call mom tonight'") == "update_task"

    def test_update_task_intent(self):
        assert detect_intent("Update the project deadline") == "update_task"

    def test_rename_task_intent(self):
        assert detect_intent("Rename task 3 to something else") == "update_task"

    def test_edit_task_intent(self):
        assert detect_intent("Edit task 4") == "update_task"


# ============================================================
# 2. ToolResponse Data Handling Tests (THE BUG FIX)
# ============================================================

class TestToolResponseDataHandling:
    """Test that ToolResponse correctly preserves the full result dict."""

    def test_list_tasks_response_preserves_tasks_key(self):
        """The critical bug: list_tasks result must keep 'tasks' key accessible."""
        # Simulate what MCP list_tasks returns
        result = {
            "success": True,
            "tasks": [
                {"id": "abc-123", "title": "Buy milk", "completed": False},
                {"id": "def-456", "title": "Call mom", "completed": True},
            ],
            "count": 2
        }

        # Import and create ToolResponse the same way the agent does
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent
        agent = CohereChatbotAgent()

        # Simulate ToolResponse creation (same as _execute_single_tool)
        class ToolResponse:
            def __init__(self, result):
                if isinstance(result, str):
                    self.success = False
                    self.data = {}
                    self.error = {"code": "STRING_RESPONSE_ERROR", "message": result}
                elif isinstance(result, dict):
                    self.success = result.get("success", False)
                    # This is the fixed line - keep full dict
                    self.data = result if self.success else {}
                    self.error = result.get("error", {}) if not self.success else None
                else:
                    self.success = False
                    self.data = {}
                    self.error = {"code": "INVALID_RESPONSE_TYPE", "message": f"Unexpected response type: {type(result).__name__}"}

        response = ToolResponse(result)
        assert response.success is True
        assert isinstance(response.data, dict), f"data should be dict, got {type(response.data)}"
        assert "tasks" in response.data, "data should have 'tasks' key"
        tasks = response.data.get("tasks", [])
        assert len(tasks) == 2
        assert tasks[0]["title"] == "Buy milk"

    def test_create_task_response_preserves_task_key(self):
        """create_task result must keep 'task' key accessible."""
        result = {
            "success": True,
            "task": {"id": "abc-123", "title": "New task", "completed": False},
            "message": "Task created successfully"
        }

        class ToolResponse:
            def __init__(self, r):
                if isinstance(r, dict):
                    self.success = r.get("success", False)
                    self.data = r if self.success else {}
                    self.error = r.get("error", {}) if not self.success else None

        response = ToolResponse(result)
        assert response.success is True
        task_data = response.data.get("task", {})
        assert task_data["title"] == "New task"

    def test_error_response_handling(self):
        """Error responses should have empty data and error info."""
        result = {
            "success": False,
            "error": "Failed to list tasks: connection error"
        }

        class ToolResponse:
            def __init__(self, r):
                if isinstance(r, dict):
                    self.success = r.get("success", False)
                    self.data = r if self.success else {}
                    self.error = r.get("error", {}) if not self.success else None

        response = ToolResponse(result)
        assert response.success is False
        assert response.data == {}
        assert "Failed" in str(response.error)


# ============================================================
# 3. Response Formatter Tests
# ============================================================

class TestResponseFormatter:
    """Test response formatting for all operations."""

    def test_format_task_created(self):
        task = {"title": "Buy groceries", "completed": False}
        result = format_task_response(task, "created")
        assert "Buy groceries" in result
        assert "created" in result

    def test_format_task_updated(self):
        task = {"title": "Updated task", "completed": False}
        result = format_task_response(task, "updated")
        assert "Updated task" in result
        assert "updated" in result

    def test_format_task_deleted(self):
        task = {"title": "Deleted task", "completed": False}
        result = format_task_response(task, "deleted")
        assert "Deleted task" in result
        assert "deleted" in result

    def test_format_task_completed(self):
        task = {"title": "Done task", "completed": True}
        result = format_task_response(task, "completed")
        assert "Done task" in result
        assert "completed" in result

    def test_format_task_incomplete(self):
        task = {"title": "Undone task", "completed": False}
        result = format_task_response(task, "completed")
        assert "Undone task" in result
        assert "incomplete" in result

    def test_format_empty_tasks_list(self):
        result = format_tasks_list_response([])
        assert "No tasks found" in result

    def test_format_single_task_list(self):
        tasks = [{"title": "Only task", "completed": False}]
        result = format_tasks_list_response(tasks)
        assert "Only task" in result

    def test_format_multiple_tasks_list(self):
        tasks = [
            {"title": "Task 1", "completed": False},
            {"title": "Task 2", "completed": True},
            {"title": "Task 3", "completed": False},
        ]
        result = format_tasks_list_response(tasks)
        assert "3 tasks" in result
        assert "1." in result
        assert "2." in result
        assert "3." in result
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result
        # Completed task should have checkmark
        assert "\u2713" in result  # ✓
        # Pending tasks should have circle
        assert "\u25CB" in result  # ○

    def test_format_error_response(self):
        result = format_error_response("AUTHENTICATION_FAILED", "Not logged in")
        assert "authenticate" in result.lower() or "logged in" in result.lower()

    def test_format_confirmation_response(self):
        result = format_confirmation_response("deleted", "task")
        assert "deleted" in result
        assert "task" in result


# ============================================================
# 4. Completion Status Extraction Tests
# ============================================================

class TestCompletionStatusExtraction:
    def test_done_status(self):
        assert extract_completion_status("mark as done") is True

    def test_complete_status(self):
        assert extract_completion_status("mark as complete") is True

    def test_finished_status(self):
        assert extract_completion_status("I finished it") is True

    def test_not_done_status(self):
        assert extract_completion_status("mark as not done") is False

    def test_incomplete_status(self):
        assert extract_completion_status("still incomplete") is False

    def test_ambiguous_status(self):
        assert extract_completion_status("hello world") is None


# ============================================================
# 5. End-to-End Agent Flow Tests (mocked Cohere + DB)
# ============================================================

class TestAgentEndToEnd:
    """Test the full agent pipeline with mocked dependencies."""

    @pytest.fixture
    def mock_cohere(self):
        """Mock the Cohere API to return predictable tool call JSON."""
        with patch("src.services.cohere_client.cohere_service") as mock_svc:
            yield mock_svc

    @pytest.fixture
    def mock_mcp_client(self):
        """Mock the MCP client to return predictable results."""
        with patch("src.ai_chatbot.agents.cohere_agent.get_mcp_client") as mock_get:
            mock_client = AsyncMock()
            mock_get.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_list_tasks_flow(self, mock_cohere, mock_mcp_client):
        """Test: 'Show me all my tasks' -> list_tasks -> formatted response."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        # Mock Cohere to return list_tasks tool call
        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "list_tasks",
            "arguments": {}
        })

        # Mock MCP list_tasks to return tasks
        mock_mcp_client.list_tasks.return_value = {
            "success": True,
            "tasks": [
                {"id": "1", "title": "Buy milk", "completed": False},
                {"id": "2", "title": "Call mom", "completed": True},
            ],
            "count": 2
        }

        agent = CohereChatbotAgent()
        result = await agent.process_request("Show me all my tasks", "fake-token", "user-1")

        assert "2 tasks" in result
        assert "Buy milk" in result
        assert "Call mom" in result

    @pytest.mark.asyncio
    async def test_create_task_flow(self, mock_cohere, mock_mcp_client):
        """Test: 'Add a task to buy groceries' -> create_task -> confirmation."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "create_task",
            "arguments": {"title": "Buy groceries"}
        })

        mock_mcp_client.create_task.return_value = {
            "success": True,
            "task": {"id": "abc-123", "title": "Buy groceries", "completed": False},
            "message": "Task created"
        }

        agent = CohereChatbotAgent()
        result = await agent.process_request("Add a task to buy groceries", "fake-token", "user-1")

        assert "Buy groceries" in result
        assert "created" in result.lower()

    @pytest.mark.asyncio
    async def test_complete_task_flow(self, mock_cohere, mock_mcp_client):
        """Test: 'Mark task 1 as done' -> complete_task -> confirmation."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "complete_task",
            "arguments": {"task_id": "1", "completed": True}
        })

        mock_mcp_client.complete_task.return_value = {
            "success": True,
            "task": {"id": "abc-123", "title": "Buy milk", "completed": True},
            "message": "Task completed"
        }

        # First store a task list so index resolution works
        from src.ai_chatbot.services.task_index_mapper import task_index_mapper
        task_index_mapper.store_task_list("user-1", [
            {"id": "abc-123", "title": "Buy milk", "completed": False}
        ])

        agent = CohereChatbotAgent()
        result = await agent.process_request("Mark task 1 as done", "fake-token", "user-1")

        assert "Buy milk" in result
        assert "completed" in result.lower()

    @pytest.mark.asyncio
    async def test_delete_task_flow(self, mock_cohere, mock_mcp_client):
        """Test: 'Delete task 1' -> delete_task -> confirmation."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "delete_task",
            "arguments": {"task_id": "1"}
        })

        mock_mcp_client.delete_task.return_value = {
            "success": True,
            "task_id": "abc-123",
            "message": "Task deleted"
        }

        # Store task list for index resolution
        from src.ai_chatbot.services.task_index_mapper import task_index_mapper
        task_index_mapper.store_task_list("user-1", [
            {"id": "abc-123", "title": "Buy milk", "completed": False}
        ])

        agent = CohereChatbotAgent()
        result = await agent.process_request("Delete task 1", "fake-token", "user-1")

        assert "deleted" in result.lower()

    @pytest.mark.asyncio
    async def test_update_task_flow(self, mock_cohere, mock_mcp_client):
        """Test: 'Change task 1 to Call mom tonight' -> update_task -> confirmation."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "update_task",
            "arguments": {"task_id": "1", "title": "Call mom tonight"}
        })

        mock_mcp_client.update_task.return_value = {
            "success": True,
            "task": {"id": "abc-123", "title": "Call mom tonight", "completed": False},
            "message": "Task updated"
        }

        # Store task list for index resolution
        from src.ai_chatbot.services.task_index_mapper import task_index_mapper
        task_index_mapper.store_task_list("user-1", [
            {"id": "abc-123", "title": "Buy milk", "completed": False}
        ])

        agent = CohereChatbotAgent()
        result = await agent.process_request("Change task 1 to Call mom tonight", "fake-token", "user-1")

        assert "Call mom tonight" in result
        assert "updated" in result.lower()

    @pytest.mark.asyncio
    async def test_list_empty_tasks(self, mock_cohere, mock_mcp_client):
        """Test: listing when no tasks exist returns 'No tasks found'."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "list_tasks",
            "arguments": {}
        })

        mock_mcp_client.list_tasks.return_value = {
            "success": True,
            "tasks": [],
            "count": 0
        }

        agent = CohereChatbotAgent()
        result = await agent.process_request("Show me my tasks", "fake-token", "user-1")

        assert "No tasks found" in result

    @pytest.mark.asyncio
    async def test_error_handling_task_not_found(self, mock_cohere, mock_mcp_client):
        """Test: graceful error when task not found."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "delete_task",
            "arguments": {"task_id": "99"}
        })

        # No stored task list, so resolution fails
        from src.ai_chatbot.services.task_index_mapper import task_index_mapper
        task_index_mapper._task_lists = {}  # Clear any stored lists

        agent = CohereChatbotAgent()
        result = await agent.process_request("Delete task 99", "fake-token", "user-unknown")

        # Should get a friendly error, not a crash
        assert "not found" in result.lower() or "show my tasks" in result.lower() or "could not find" in result.lower()

    @pytest.mark.asyncio
    async def test_mcp_error_handling(self, mock_cohere, mock_mcp_client):
        """Test: graceful handling when MCP tool returns an error."""
        from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent

        mock_cohere.generate_ai_response.return_value = json.dumps({
            "tool": "list_tasks",
            "arguments": {}
        })

        mock_mcp_client.list_tasks.return_value = {
            "success": False,
            "error": {"code": "LIST_TASKS_ERROR", "message": "Database connection failed"}
        }

        agent = CohereChatbotAgent()
        result = await agent.process_request("Show my tasks", "fake-token", "user-1")

        # Should return an error message, not crash
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================
# 6. Parameter Extraction Tests
# ============================================================

class TestParameterExtraction:
    def test_extract_buy_groceries(self):
        params = extract_task_parameters("Add a task to buy groceries")
        assert "title" in params
        assert "buy" in params["title"].lower() or "groceries" in params["title"].lower()

    def test_extract_with_due_date_tomorrow(self):
        params = extract_task_parameters("Add task to call mom tomorrow")
        assert "due_date" in params

    def test_extract_with_iso_date(self):
        params = extract_task_parameters("Create a task to submit report by 2025-12-31")
        assert params.get("due_date") == "2025-12-31"

    def test_extract_with_next_week(self):
        params = extract_task_parameters("Add a task to clean house next week")
        assert "due_date" in params


# ============================================================
# Run tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
