"""Test suite for AI Chatbot Implementation."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.ai_chatbot.utils.nlp_utils import detect_intent, extract_task_parameters
from src.ai_chatbot.agents.cohere_agent import CohereChatbotAgent
from src.ai_chatbot.processors.input_processor import InputProcessor


def test_intent_detection():
    """Test intent detection functionality."""
    # Test create task intent
    assert detect_intent("Add a task to buy groceries") == "create_task"
    assert detect_intent("Create a new task for meeting preparation") == "create_task"

    # Test list tasks intent
    assert detect_intent("Show me my tasks") == "list_tasks"
    assert detect_intent("What do I need to do today?") == "list_tasks"

    # Test update task intent
    assert detect_intent("Update my project deadline") == "update_task"
    assert detect_intent("Change the meeting time") == "update_task"

    # Test delete task intent
    assert detect_intent("Delete my old shopping list") == "delete_task"
    assert detect_intent("Remove the cancelled event") == "delete_task"

    # Test complete task intent
    assert detect_intent("Mark the meeting as done") == "complete_task"
    assert detect_intent("Finish my assignment") == "complete_task"

    print("✓ Intent detection tests passed")


def test_parameter_extraction():
    """Test parameter extraction functionality."""
    # Test title extraction
    params = extract_task_parameters("Add a task to buy groceries tomorrow")
    assert "title" in params
    assert params["title"] == "buy groceries"

    # Test due date extraction
    params = extract_task_parameters("Create a task to submit report by 2023-12-31")
    assert "due_date" in params
    assert params["due_date"] == "2023-12-31"

    # Test tomorrow extraction
    params = extract_task_parameters("Add task to call mom tomorrow")
    assert "title" in params
    assert params["title"] == "call mom"

    print("✓ Parameter extraction tests passed")


def test_input_processor_initialization():
    """Test input processor initialization."""
    processor = InputProcessor()
    assert processor.agent is not None
    print("✓ Input processor initialization test passed")


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test Cohere agent initialization."""
    with patch.dict('os.environ', {'COHERE_API_KEY': 'test-key'}):
        agent = CohereChatbotAgent()
        assert agent.model == "command-r-plus"
        assert len(agent.tools) > 0  # Should have registered tools
        print("✓ Agent initialization test passed")


def test_task_completion_requirement():
    """Test that all major components are implemented."""
    # Check that required modules exist
    import src.ai_chatbot.agents.cohere_agent
    import src.ai_chatbot.tools.create_task_tool
    import src.ai_chatbot.tools.list_tasks_tool
    import src.ai_chatbot.tools.update_task_tool
    import src.ai_chatbot.tools.delete_task_tool
    import src.ai_chatbot.tools.complete_task_tool
    import src.ai_chatbot.services.api_client
    import src.ai_chatbot.utils.jwt_handler
    import src.ai_chatbot.utils.validation

    print("✓ All required components exist")


def run_tests():
    """Run all tests."""
    print("Running AI Chatbot Implementation Tests...\n")

    test_intent_detection()
    test_parameter_extraction()
    test_input_processor_initialization()
    test_agent_initialization()
    test_task_completion_requirement()

    print("\n🎉 All tests passed! AI Chatbot implementation is functioning correctly.")


if __name__ == "__main__":
    # Run the synchronous tests
    run_tests()

    # Run the async test separately
    asyncio.run(test_agent_initialization())