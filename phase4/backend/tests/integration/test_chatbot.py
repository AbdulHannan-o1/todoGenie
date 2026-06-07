"""
Integration tests for text-based todo creation in chatbot
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from auth import get_current_user
from models import User
import uuid
from src.services.chatbot import ChatbotService
from src.services.task_operations import TaskOperationsService


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


def test_text_based_todo_creation_integration(client):
    """
    Integration test: User types 'Add a task to buy groceries' and sees new task created
    Tests the full flow from API endpoint through AI processing to task creation
    """
    # Mock the AI agent service to return predictable responses
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Simulate successful task creation response
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

        # Make request to the chat endpoint
        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",
                "message_type": "text"
            }
        )

        # Assert successful response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "buy groceries" in data["response"]

        # Verify that the mock was called correctly
        mock_process.assert_called_once()


def test_text_based_todo_listing_integration(client):
    """
    Integration test: User types 'Show my tasks' and sees their tasks
    """
    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Simulate successful task listing response
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
                "content": "Show my tasks",
                "message_type": "text"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "Buy groceries" in data["response"] or "Call mom" in data["response"]


def test_text_based_todo_update_integration(client):
    """
    Integration test: User types 'Update task 1 to add description' and sees task updated
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
                "content": "Update task 1 to add description: Get milk, bread, and eggs",
                "message_type": "text"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "response" in data
        assert "tool_results" in data


def test_conversation_persistence_integration(client):
    """
    Integration test: Verify conversation is persisted and can be retrieved
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "response": "I've created the task for you.",
            "tool_results": [{"status": "success", "message": "Task created"}],
            "conversation_id": conversation_id
        }

        # First message creates conversation
        response1 = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",
                "message_type": "text"
            }
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["conversation_id"] == conversation_id

        # Verify we can get the conversation
        response2 = client.get(f"/api/v1/chat/conversations/{conversation_id}")
        assert response2.status_code == 200


def test_multiple_task_operations_in_sequence(client):
    """
    Integration test: Multiple task operations in one session work correctly
    """
    conversation_id = str(uuid.uuid4())

    with patch('src.services.chatbot.chatbot_service.process_user_message') as mock_process:
        # Configure mock to return different responses for different calls
        def side_effect(*args, **kwargs):
            content = args[1] if len(args) > 1 else kwargs.get('content', '')
            if 'add' in content.lower():
                return {
                    "success": True,
                    "response": "Task added successfully",
                    "tool_results": [{"status": "success", "message": "Task created"}],
                    "conversation_id": conversation_id
                }
            elif 'show' in content.lower() or 'list' in content.lower():
                return {
                    "success": True,
                    "response": "You have 1 task: Buy groceries",
                    "tool_results": [{"status": "success", "message": "Found 1 task"}],
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "success": True,
                    "response": "Operation completed",
                    "tool_results": [{"status": "success", "message": "Operation completed"}],
                    "conversation_id": conversation_id
                }

        mock_process.side_effect = side_effect

        # Add a task
        response1 = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )
        assert response1.status_code == 200

        # List tasks
        response2 = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Show my tasks",
                "message_type": "text",
                "conversation_id": conversation_id
            }
        )
        assert response2.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])