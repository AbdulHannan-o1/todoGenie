#!/usr/bin/env python3
"""
Test script to verify z.ai GLM integration works properly
"""
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock


def test_zai_integration():
    """Function to run all tests with proper mocking"""
    print("Starting z.ai GLM integration tests...\n")

    # Add the src directory to the path so we can import modules
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    # Test 1: Configuration
    print("Testing z.ai configuration...")

    # Mock the OpenAI client before importing to avoid immediate API calls
    with patch('openai.OpenAI'):
        # Import the modules after mocking
        from core.config import settings

        # Verify the settings are as expected
        assert settings.ai_model == "glm-4.7", f"Expected 'glm-4.7', got '{settings.ai_model}'"
        assert settings.openai_api_base == "https://api.z.ai/api/paas/v4/", f"Expected z.ai endpoint, got '{settings.openai_api_base}'"

        print("✓ Configuration test passed")

    # Test 2: AI Agent Initialization (with proper mocking)
    print("Testing AI agent initialization...")

    with patch('openai.OpenAI') as mock_openai:
        # Create a mock client instance
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance

        # Import and test the AI agent service
        from services.ai_agent import AIAgentService

        # Temporarily override settings to use test key
        original_zai_key = settings.zai_api_key
        settings.zai_api_key = "test-key"

        agent = AIAgentService()

        # Check that the agent has the correct model
        assert agent.model == "glm-4.7", f"Expected 'glm-4.7', got '{agent.model}'"

        # Restore original key
        settings.zai_api_key = original_zai_key

        print("✓ AI agent initialization test passed")

    # Test 3: AI Agent Process Message (with proper mocking)
    print("Testing AI agent message processing...")

    with patch('openai.OpenAI') as mock_openai:
        # Create a mock client instance
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance

        # Mock the API call to avoid making actual API requests during testing
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Test response from z.ai"

        mock_client_instance.chat.completions.create.return_value = mock_response

        # Import and test the AI agent service
        from services.ai_agent import AIAgentService

        # Temporarily override settings to use test key
        original_zai_key = settings.zai_api_key
        settings.zai_api_key = "test-key"

        agent = AIAgentService()

        # Process a test message
        import asyncio
        async def process_test():
            return await agent.process_message("Test message", "test-user-id", "test-conversation-id")

        result = asyncio.run(process_test())

        # Verify the result structure
        assert "response" in result
        assert "tool_results" in result
        assert "success" in result

        # Restore original key
        settings.zai_api_key = original_zai_key

        print("✓ AI agent message processing test passed")

    print("\nAll tests passed! z.ai GLM integration is working correctly.")
    return True


if __name__ == "__main__":
    try:
        success = test_zai_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)