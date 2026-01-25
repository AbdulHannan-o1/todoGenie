#!/usr/bin/env python3
"""
Test script to validate response quality and performance of z.ai GLM integration
"""
import os
import sys
import asyncio
import time
from unittest.mock import patch, MagicMock
import json


def test_response_quality_and_performance():
    """Function to validate response quality and performance with z.ai integration"""
    print("Starting response quality and performance validation tests...\n")

    # Add the src directory to the path so we can import modules
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    print("Testing response quality and performance...")

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

        # Mock response that simulates z.ai response with function calling
        mock_response_with_tool = MagicMock()
        mock_response_with_tool.choices = [MagicMock()]
        mock_response_with_tool.choices[0].message = MagicMock()

        # Create a mock tool call for create_task
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "create_task"
        mock_tool_call.function.arguments = json.dumps({"title": "Test task", "description": "Test description", "user_id": "test-user"})

        mock_response_with_tool.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_with_tool.choices[0].message.content = "I'll create a task for you."

        # Mock the final response after tool execution
        mock_final_response = MagicMock()
        mock_final_response.choices = [MagicMock()]
        mock_final_response.choices[0].message = MagicMock()
        mock_final_response.choices[0].message.content = "I've created the task 'Test task' for you."

        # Set up the mock to return different responses for different calls
        def side_effect(*args, **kwargs):
            # Check if this is the second call (after tool execution)
            messages = kwargs.get('messages', [])
            if any('tool' in msg.get('role', '') for msg in messages):
                return mock_final_response
            else:
                return mock_response_with_tool

        mock_client_instance.chat.completions.create.side_effect = side_effect

        agent = AIAgentService()

        # Test 1: Response Quality - Check that responses contain expected elements
        print("Testing response quality...")

        start_time = time.time()
        result = asyncio.run(agent.process_message("Add a task to test the system", "test-user-id", "test-conversation-id"))
        processing_time = time.time() - start_time

        # Verify the response structure
        assert "response" in result
        assert "tool_results" in result
        assert "success" in result
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0  # Response should not be empty
        assert isinstance(result["tool_results"], list)

        print(f"✓ Response quality test passed - Response length: {len(result['response'])} chars")

        # Test 2: Performance - Check that processing time is reasonable
        print("Testing performance...")

        assert processing_time < 5.0, f"Processing took too long: {processing_time:.2f}s"  # Less than 5 seconds
        print(f"✓ Performance test passed - Processing time: {processing_time:.3f}s")

        # Test 3: Function calling capability
        print("Testing function calling capability...")

        # Verify that tool results were processed correctly
        assert len(result["tool_results"]) > 0, "Should have at least one tool result"
        print("✓ Function calling capability test passed")

        # Test 4: Error handling
        print("Testing error handling...")

        # Mock an error response from the API
        mock_error_response = MagicMock()
        mock_error_response.choices = [MagicMock()]
        mock_error_response.choices[0].message = MagicMock()
        mock_error_response.choices[0].message.tool_calls = None
        mock_error_response.choices[0].message.content = "Test response"

        def error_side_effect(*args, **kwargs):
            raise Exception("API Error")

        mock_client_instance.chat.completions.create.side_effect = error_side_effect

        error_result = asyncio.run(agent.process_message("Test error handling", "test-user-id", "test-conversation-id"))

        # Verify error handling
        assert "error" in error_result or not error_result["success"], "Should handle errors gracefully"
        print("✓ Error handling test passed")

        # Test 5: Multiple operations in sequence
        print("Testing multiple operations in sequence...")

        # Reset the mock to normal behavior
        mock_client_instance.chat.completions.create.side_effect = side_effect

        # Test a sequence of operations
        operations = [
            "Add a task to buy groceries",
            "Show me my tasks",
            "Update task 1 to add description",
            "Mark task 1 as complete"
        ]

        for i, operation in enumerate(operations):
            op_result = asyncio.run(agent.process_message(operation, f"test-user-{i}", f"test-conversation-{i}"))
            assert "response" in op_result
            assert "tool_results" in op_result

        print("✓ Multiple operations test passed")

        # Restore original key
        settings.zai_api_key = original_zai_key

        print(f"\nAll response quality and performance tests passed!")
        print(f"✓ Response quality maintained")
        print(f"✓ Performance within acceptable limits")
        print(f"✓ Function calling working correctly")
        print(f"✓ Error handling working properly")
        print(f"✓ Multiple operations supported")

        return True


if __name__ == "__main__":
    try:
        success = test_response_quality_and_performance()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)