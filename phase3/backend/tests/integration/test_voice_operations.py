"""
Integration tests for voice-based task operations
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from auth import get_current_user
from models import User
import uuid


@pytest.fixture
def client():
    """Create a test client with authenticated user"""
    with TestClient(app) as test_client:
        # Mock the authentication dependency
        def mock_get_current_user():
            mock_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                name="Test User",
                password="hashed_password"
            )
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        yield test_client
        app.dependency_overrides.clear()


def test_voice_based_task_listing_integration(client):
    """
    Integration test: User says "Show me all my tasks" and sees their tasks
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "You have 2 tasks: 1. Buy groceries, 2. Call mom",
            "tool_results": [{
                "status": "success",
                "message": "Found 2 tasks",
                "tasks": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Buy groceries",
                        "description": None,
                        "status": "pending",
                        "priority": "medium",
                        "due_date": None
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Call mom",
                        "description": "Call mother for her birthday",
                        "status": "pending",
                        "priority": "high",
                        "due_date": "2023-12-25T10:00:00"
                    }
                ]
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Show me all my tasks",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "Buy groceries" in data["response"] or "Call mom" in data["response"]


def test_voice_based_task_creation_integration(client):
    """
    Integration test: User says "Add a task to buy groceries" and task is created
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "I've created the task 'buy groceries' for you.",
            "tool_results": [{
                "status": "success",
                "message": "Task 'buy groceries' created successfully",
                "task_id": str(uuid.uuid4()),
                "task": {
                    "id": str(uuid.uuid4()),
                    "title": "buy groceries",
                    "description": None,
                    "status": "pending"
                }
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "buy groceries" in data["response"]


def test_voice_based_task_completion_integration(client):
    """
    Integration test: User says "Mark task 3 as complete" and task is updated
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "I've marked task 3 as complete.",
            "tool_results": [{
                "status": "success",
                "message": "Task updated successfully",
                "task": {
                    "id": str(uuid.uuid4()),
                    "title": "Buy groceries",
                    "description": None,
                    "status": "completed"
                }
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 3 as complete",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "complete" in data["response"]


def test_voice_based_task_update_integration(client):
    """
    Integration test: User says "Update task 1 to add description" and task is updated
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "I've updated the task 'Buy groceries' with the new description.",
            "tool_results": [{
                "status": "success",
                "message": "Task 'Buy groceries' updated successfully",
                "task": {
                    "id": str(uuid.uuid4()),
                    "title": "Buy groceries",
                    "description": "Get milk, bread, and eggs",
                    "status": "pending"
                }
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Update task 1 to add description: Get milk, bread, and eggs",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data


def test_voice_based_task_deletion_integration(client):
    """
    Integration test: User says "Delete task 2" and task is deleted
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "I've deleted the task 'Call mom'.",
            "tool_results": [{
                "status": "success",
                "message": "Task 'Call mom' deleted successfully"
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Delete task 2",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "deleted" in data["response"]


def test_voice_command_error_handling_integration(client):
    """
    Integration test: Voice commands with invalid task IDs are handled gracefully
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Simulate an error response when an invalid task ID is provided
        mock_process.return_value = {
            "success": False,
            "response": "I couldn't find task 999. Please check the task number and try again.",
            "tool_results": [{
                "status": "error",
                "message": "Task with ID 999 not found"
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 999 as complete",  # Non-existent task
                "message_type": "voice"
            }
        )

        assert response.status_code == 200  # Should still return 200, but with error in tool_results
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        # The AI should provide helpful feedback about the invalid task


def test_voice_command_validation_integration(client):
    """
    Integration test: Voice command validation works properly for task operations
    """
    # Test that the backend properly validates voice commands
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Test a command that should result in task listing
        mock_process.return_value = {
            "success": True,
            "response": "You have 1 task: 1. Buy groceries",
            "tool_results": [{
                "status": "success",
                "message": "Found 1 task",
                "tasks": [{"id": str(uuid.uuid4()), "title": "Buy groceries", "status": "pending"}]
            }],
            "conversation_id": str(uuid.uuid4())
        }

        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "What are my tasks?",  # Various ways to ask for tasks
                "message_type": "voice"
            }
        )
        assert response.status_code == 200


def test_conversation_preservation_with_voice_commands(client):
    """
    Integration test: Conversation context is preserved between voice commands
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        call_count = 0

        def side_effect(user_id, content, message_type, conversation_id_param):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First voice command: List tasks
                return {
                    "success": True,
                    "response": "You have 1 task: 1. Buy groceries",
                    "tool_results": [{
                        "status": "success",
                        "message": "Found 1 task",
                        "tasks": [{"id": "task1", "title": "Buy groceries", "status": "pending"}]
                    }],
                    "conversation_id": conversation_id_param
                }
            elif call_count == 2:
                # Second voice command: Update the specific task
                return {
                    "success": True,
                    "response": "I've marked 'Buy groceries' as complete.",
                    "tool_results": [{
                        "status": "success",
                        "message": "Task updated successfully",
                        "task": {"id": "task1", "title": "Buy groceries", "status": "completed"}
                    }],
                    "conversation_id": conversation_id_param
                }
            else:
                return {
                    "success": True,
                    "response": "Operation processed.",
                    "tool_results": [{"status": "success", "message": "Operation completed"}],
                    "conversation_id": conversation_id_param
                }

        mock_process.side_effect = side_effect

        # First voice command: List tasks
        response1 = client.post(
            "/api/v1/chat/send",
            json={
                "content": "What are my tasks?",
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )
        assert response1.status_code == 200

        # Second voice command: Update task (in same conversation)
        response2 = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Mark task 1 as complete",
                "message_type": "voice",
                "conversation_id": conversation_id
            }
        )
        assert response2.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])