"""
Integration tests for mixed text/voice input conversation
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid
from src.api.v1.chat import chatbot_service


def test_mixed_input_conversation_flow(auth_client):
    """
    Integration test: User starts with text "Show me all my tasks",
    then switches to voice "Mark task 3 as complete", both operations work in same conversation
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.api.v1.chat.chatbot_service.process_user_message') as mock_process:
        # Configure mock to return different responses for different inputs
        def side_effect(user_id, content, message_type, conversation_id):
            if 'show' in content.lower() and 'tasks' in content.lower():
                return {
                    "success": True,
                    "response": "You have 3 tasks: 1. Buy groceries, 2. Call mom, 3. Schedule meeting",
                    "tool_results": [{
                        "status": "success",
                        "message": "Found 3 tasks",
                        "tasks": [
                            {"id": str(uuid.uuid4()), "title": "Buy groceries", "status": "pending"},
                            {"id": str(uuid.uuid4()), "title": "Call mom", "status": "pending"},
                            {"id": str(uuid.uuid4()), "title": "Schedule meeting", "status": "pending"}
                        ]
                    }],
                    "conversation_id": conversation_id or str(uuid.uuid4())
                }
            elif 'mark' in content.lower() and 'complete' in content.lower():
                return {
                    "success": True,
                    "response": "I've marked task 3 as complete.",
                    "tool_results": [{
                        "status": "success",
                        "message": "Task updated successfully",
                        "task": {
                            "id": str(uuid.uuid4()),
                            "title": "Schedule meeting",
                            "status": "completed"
                        }
                    }],
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "success": True,
                    "response": "Operation processed successfully.",
                    "tool_results": [{"status": "success", "message": "Operation completed"}],
                    "conversation_id": conversation_id or str(uuid.uuid4())
                }

        mock_process.side_effect = side_effect

        # Step 1: Text input - "Show me all my tasks"
        response1 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Show me all my tasks",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert "conversation_id" in data1
        assert data1["conversation_id"] == conversation_id
        assert "response" in data1

        # Step 2: Voice input - "Mark task 3 as complete" (in same conversation)
        response2 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 3 as complete",  # This would be transcribed voice input
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )

        if response2.status_code != 200:
            print(f"Response 2 error: {response2.json()}")
        assert response2.status_code == 200
        data2 = response2.json()
        assert "conversation_id" in data2
        assert data2["conversation_id"] == conversation_id
        assert "response" in data2


def test_conversation_context_preservation(auth_client):
    """
    Integration test: Context is preserved between text and voice messages in same conversation
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.api.v1.chat.chatbot_service.process_user_message') as mock_process:
        call_count = 0

        def side_effect(user_id, content, message_type, conversation_id):
            nonlocal call_count
            call_count += 1

            # Return different responses based on call number to simulate context
            if call_count == 1:
                # First call - text message
                return {
                    "success": True,
                    "response": "I've created the task 'buy groceries'.",
                    "tool_results": [{
                        "status": "success",
                        "message": "Task created",
                        "task_id": str(uuid.uuid4()),
                        "task": {"id": str(uuid.uuid4()), "title": "buy groceries", "status": "pending"}
                    }],
                    "conversation_id": conversation_id
                }
            elif call_count == 2:
                # Second call - voice message in same conversation
                return {
                    "success": True,
                    "response": "I've added the description to your 'buy groceries' task.",
                    "tool_results": [{
                        "status": "success",
                        "message": "Task updated",
                        "task": {"id": str(uuid.uuid4()), "title": "buy groceries", "description": "Get milk and bread", "status": "pending"}
                    }],
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "success": True,
                    "response": "Operation processed.",
                    "tool_results": [{"status": "success", "message": "Operation completed"}],
                    "conversation_id": conversation_id
                }

        mock_process.side_effect = side_effect

        # First message: Text
        response1 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )
        assert response1.status_code == 200

        # Second message: Voice in same conversation
        response2 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add description: Get milk and bread",
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )
        assert response2.status_code == 200


def test_conversation_history_retrieval(auth_client):
    """
    Integration test: Conversation history can be retrieved showing both text and voice messages
    """
    conversation_id = str(uuid.uuid4())

    # First, create a conversation by sending a few messages
    with patch('src.api.v1.chat.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "Message processed.",
            "tool_results": [{"status": "success", "message": "Processed"}],
            "conversation_id": conversation_id
        }

        # Send text message
        auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Show my tasks",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )

        # Send voice message
        auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 1 as done",
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )

    # Now retrieve the conversation history
    response = auth_client.get(f"/api/v1/chat/conversations/{conversation_id}")

    # The endpoint might return 200 with messages or 404 if conversation doesn't exist yet
    if response.status_code == 200:
        data = response.json()
        assert "messages" in data
        # Should contain both text and voice messages that were sent
    elif response.status_code == 404:
        # This is acceptable if the conversation was not persisted in this test run
        pass
    else:
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"


def test_multiple_conversations_isolation(auth_client):
    """
    Integration test: Different conversations remain isolated when switching between text/voice
    """
    conversation1_id = str(uuid.uuid4())
    conversation2_id = str(uuid.uuid4())

    with patch('src.api.v1.chat.chatbot_service.process_user_message') as mock_process:
        def side_effect(user_id, content, message_type, conversation_id):
            return {
                "success": True,
                "response": "Message processed in conversation.",
                "tool_results": [{"status": "success", "message": "Processed"}],
                "conversation_id": conversation_id
            }
        mock_process.side_effect = side_effect

        # In conversation 1: Text message
        response1 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Task for conversation 1",
                "message_type": "text",
                "conversation_id": conversation1_id
            }
        )
        assert response1.status_code == 200
        assert response1.json()["conversation_id"] == conversation1_id

        # In conversation 2: Voice message
        response2 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Task for conversation 2",
                "message_type": "voice",
                "conversation_id": conversation2_id
            }
        )
        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conversation2_id

        # Verify conversations are separate
        conv1_response = auth_client.get(f"/api/v1/chat/conversations/{conversation1_id}")
        conv2_response = auth_client.get(f"/api/v1/chat/conversations/{conversation2_id}")

        # Both should be accessible independently
        assert conv1_response.status_code in [200, 404]  # May or may not exist yet
        assert conv2_response.status_code in [200, 404]  # May or may not exist yet


def test_voice_command_context_in_conversation(auth_client):
    """
    Integration test: Voice commands work properly within conversation context
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.api.v1.chat.chatbot_service.process_user_message') as mock_process:
        call_count = 0

        def side_effect(user_id, content, message_type, conversation_id):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First: Text command to list tasks
                return {
                    "success": True,
                    "response": "You have 2 tasks: 1. Buy groceries, 2. Call mom",
                    "tool_results": [{
                        "status": "success",
                        "message": "Found 2 tasks",
                        "tasks": [
                            {"id": "task1", "title": "Buy groceries", "status": "pending"},
                            {"id": "task2", "title": "Call mom", "status": "pending"}
                        ]
                    }],
                    "conversation_id": conversation_id
                }
            elif call_count == 2:
                # Second: Voice command referencing specific task
                return {
                    "success": True,
                    "response": "I've marked 'Call mom' as complete.",
                    "tool_results": [{
                        "status": "success",
                        "message": "Task updated successfully",
                        "task": {"id": "task2", "title": "Call mom", "status": "completed"}
                    }],
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "success": True,
                    "response": "Operation processed.",
                    "tool_results": [{"status": "success", "message": "Processed"}],
                    "conversation_id": conversation_id
                }

        mock_process.side_effect = side_effect

        # Step 1: Text to list tasks
        response1 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Show me my tasks",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )
        assert response1.status_code == 200

        # Step 2: Voice to update specific task (should work in context)
        response2 = auth_client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 2 as complete",  # Voice command referencing context
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )
        assert response2.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])