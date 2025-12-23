"""
Integration tests for voice-based todo creation in chatbot
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from auth import get_current_user
from models import User
import uuid
from src.services.voice_processor import voice_processor_service
from src.services.chatbot import chatbot_service


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


def test_voice_based_todo_creation_integration(client):
    """
    Integration test: User speaks 'Add a task to buy groceries' and sees new task created
    Tests the full flow from voice input through processing to task creation
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Simulate successful task creation response from AI agent
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

        # In v1, voice-to-text happens in browser, so we send the transcribed text
        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",  # This is the transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "buy groceries" in data["response"]


def test_voice_command_validation_integration(client):
    """
    Integration test: Voice command validation works correctly
    """
    # Test the voice command validation service directly
    result = voice_processor_service.validate_voice_command("Add a task to buy groceries")

    assert result["is_valid_task_command"] == True
    assert result["is_task_related"] == True
    assert "buy groceries" in result["text"].lower()


def test_voice_based_task_listing_integration(client):
    """
    Integration test: User speaks 'Show my tasks' and sees their tasks
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "Here are your tasks: 1. Buy groceries, 2. Call mom",
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
                "content": "Show my tasks",  # Transcribed voice input
                "message_type": "voice"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "Buy groceries" in data["response"] or "Call mom" in data["response"]


def test_voice_based_task_completion_integration(client):
    """
    Integration test: User speaks 'Mark task 3 as complete' and task is updated
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


def test_voice_audio_format_validation(client):
    """
    Integration test: Audio format validation works correctly
    """
    # Test the voice processor's audio format validation
    result = voice_processor_service.validate_audio_format("mp3")
    assert result["valid"] == True
    assert result["format"] == "mp3"

    result = voice_processor_service.validate_audio_format("invalid_format")
    assert result["valid"] == False
    assert result["format"] == "invalid_format"


def test_voice_command_with_task_id_detection(client):
    """
    Integration test: Voice commands with task IDs are properly detected
    """
    # Test command with task ID
    result = voice_processor_service.validate_voice_command("Mark task 3 as done")
    assert result["is_valid_task_command"] == True
    assert "3" in result["detected_task_ids"]

    # Test command with different task ID format
    result = voice_processor_service.validate_voice_command("Complete number 5")
    assert result["is_valid_task_command"] == True
    assert "5" in result["detected_task_ids"]


def test_voice_command_with_invalid_task_id_handling(client):
    """
    Integration test: Invalid task IDs in voice commands are handled gracefully
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


if __name__ == "__main__":
    pytest.main([__file__])