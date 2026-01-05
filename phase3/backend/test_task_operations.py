#!/usr/bin/env python3
"""
Test script to verify z.ai GLM integration works properly with task operations
"""
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock
import json


def test_task_operations():
    """Function to test task operations with z.ai integration"""
    print("Starting task operations tests with z.ai GLM integration...\n")

    # Add the src directory to the path so we can import modules
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    print("Testing task operations with function calling...")

    with patch('openai.OpenAI') as mock_openai:
        # Create a mock client instance
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance

        # Import the modules after mocking
        from core.config import settings
        from services.ai_agent import AIAgentService

        # Temporarily override settings to use test key
        original_zai_key = settings.zai_api_key
        settings.zai_api_key = "test-key"

        # Test 1: Create task operation
        print("Testing create task operation...")

        # Mock response that simulates z.ai response with tool calling for create_task
        mock_response_create = MagicMock()
        mock_response_create.choices = [MagicMock()]
        mock_response_create.choices[0].message = MagicMock()

        # Create a mock tool call for create_task
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "create_task"
        mock_tool_call.function.arguments = json.dumps({"title": "Buy groceries", "description": "Milk, bread, eggs"})

        # Set up tool calls in the response
        mock_response_create.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_create.choices[0].message.content = "Creating a task to buy groceries"

        # Mock the second call (after tool execution)
        mock_final_response = MagicMock()
        mock_final_response.choices = [MagicMock()]
        mock_final_response.choices[0].message = MagicMock()
        mock_final_response.choices[0].message.content = "I've created the task 'Buy groceries' for you."

        # Set up the mock to return different responses for different calls
        def side_effect(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_create

        mock_client_instance.chat.completions.create.side_effect = side_effect

        agent = AIAgentService()

        # Process a message that should trigger create_task
        result = asyncio.run(agent.process_message("Add a task to buy groceries with description: Milk, bread, eggs", "test-user-id", "test-conversation-id"))

        # Verify the result contains tool results
        assert "tool_results" in result
        assert len(result["tool_results"]) > 0
        print("✓ Create task operation test passed")

        # Test 2: List tasks operation
        print("Testing list tasks operation...")

        # Reset the mock for the next test
        mock_response_list = MagicMock()
        mock_response_list.choices = [MagicMock()]
        mock_response_list.choices[0].message = MagicMock()

        # Create a mock tool call for list_tasks
        mock_tool_call_list = MagicMock()
        mock_tool_call_list.id = "call_456"
        mock_tool_call_list.function = MagicMock()
        mock_tool_call_list.function.name = "list_tasks"
        mock_tool_call_list.function.arguments = json.dumps({})

        mock_response_list.choices[0].message.tool_calls = [mock_tool_call_list]
        mock_response_list.choices[0].message.content = "Listing your tasks"

        # Set up the mock to return different responses for different calls
        def side_effect_list(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_list

        mock_client_instance.chat.completions.create.side_effect = side_effect_list

        # Process a message that should trigger list_tasks
        result = asyncio.run(agent.process_message("Show me my tasks", "test-user-id", "test-conversation-id"))

        # Verify the result structure
        assert "tool_results" in result
        assert "response" in result
        print("✓ List tasks operation test passed")

        # Test 3: Update task operation
        print("Testing update task operation...")

        # Reset the mock for the next test
        mock_response_update = MagicMock()
        mock_response_update.choices = [MagicMock()]
        mock_response_update.choices[0].message = MagicMock()

        # Create a mock tool call for update_task
        mock_tool_call_update = MagicMock()
        mock_tool_call_update.id = "call_789"
        mock_tool_call_update.function = MagicMock()
        mock_tool_call_update.function.name = "update_task"
        mock_tool_call_update.function.arguments = json.dumps({"task_id": "1", "title": "Updated task", "description": "Updated description"})

        mock_response_update.choices[0].message.tool_calls = [mock_tool_call_update]
        mock_response_update.choices[0].message.content = "Updating your task"

        # Set up the mock to return different responses for different calls
        def side_effect_update(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_update

        mock_client_instance.chat.completions.create.side_effect = side_effect_update

        # Process a message that should trigger update_task
        result = asyncio.run(agent.process_message("Update task 1 to have title 'Updated task' and description 'Updated description'", "test-user-id", "test-conversation-id"))

        # Verify the result structure
        assert "tool_results" in result
        print("✓ Update task operation test passed")

        # Test 4: Delete task operation
        print("Testing delete task operation...")

        # Reset the mock for the next test
        mock_response_delete = MagicMock()
        mock_response_delete.choices = [MagicMock()]
        mock_response_delete.choices[0].message = MagicMock()

        # Create a mock tool call for delete_task
        mock_tool_call_delete = MagicMock()
        mock_tool_call_delete.id = "call_abc"
        mock_tool_call_delete.function = MagicMock()
        mock_tool_call_delete.function.name = "delete_task"
        mock_tool_call_delete.function.arguments = json.dumps({"task_id": "1"})

        mock_response_delete.choices[0].message.tool_calls = [mock_tool_call_delete]
        mock_response_delete.choices[0].message.content = "Deleting your task"

        # Set up the mock to return different responses for different calls
        def side_effect_delete(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_delete

        mock_client_instance.chat.completions.create.side_effect = side_effect_delete

        # Process a message that should trigger delete_task
        result = asyncio.run(agent.process_message("Delete task 1", "test-user-id", "test-conversation-id"))

        # Verify the result structure
        assert "tool_results" in result
        print("✓ Delete task operation test passed")

        # Test 5: Complete task operation
        print("Testing complete task operation...")

        # Reset the mock for the next test
        mock_response_complete = MagicMock()
        mock_response_complete.choices = [MagicMock()]
        mock_response_complete.choices[0].message = MagicMock()

        # Create a mock tool call for complete_task
        mock_tool_call_complete = MagicMock()
        mock_tool_call_complete.id = "call_def"
        mock_tool_call_complete.function = MagicMock()
        mock_tool_call_complete.function.name = "complete_task"
        mock_tool_call_complete.function.arguments = json.dumps({"task_id": "1", "completed": True})

        mock_response_complete.choices[0].message.tool_calls = [mock_tool_call_complete]
        mock_response_complete.choices[0].message.content = "Completing your task"

        # Set up the mock to return different responses for different calls
        def side_effect_complete(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_complete

        mock_client_instance.chat.completions.create.side_effect = side_effect_complete

        # Process a message that should trigger complete_task
        result = asyncio.run(agent.process_message("Mark task 1 as complete", "test-user-id", "test-conversation-id"))

        # Verify the result structure
        assert "tool_results" in result
        print("✓ Complete task operation test passed")

        # Restore original key
        settings.zai_api_key = original_zai_key

        print("\nAll task operations tests passed! z.ai GLM integration works correctly with function calling.")
        return True


if __name__ == "__main__":
    try:
        success = test_task_operations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)