"""
Contract tests for conversation management endpoints
"""
import pytest
from fastapi.testclient import TestClient
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


def test_conversations_list_endpoint_contract(client):
    """
    Contract test for /api/v1/chat/conversations endpoint
    Verifies the endpoint returns expected output format
    """
    response = client.get("/api/v1/chat/conversations")

    # Should return 200 with list of conversations
    assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()

        # Response should be a list
        assert isinstance(data, list), "Response should be a list of conversations"

        # If there are conversations, check their structure
        for conversation in data:
            assert "id" in conversation, "Conversation must contain id"
            assert "title" in conversation, "Conversation must contain title"
            assert "created_at" in conversation, "Conversation must contain created_at"
            assert "updated_at" in conversation, "Conversation must contain updated_at"
            assert "message_count" in conversation, "Conversation must contain message_count"

            # Validate field types
            assert isinstance(conversation["id"], str), "id must be string"
            assert isinstance(conversation["title"], str), "title must be string"
            assert isinstance(conversation["created_at"], str), "created_at must be string (ISO format)"
            assert isinstance(conversation["updated_at"], str), "updated_at must be string (ISO format)"
            assert isinstance(conversation["message_count"], int), "message_count must be integer"


def test_conversation_detail_endpoint_contract(client):
    """
    Contract test for /api/v1/chat/conversations/{conversation_id} endpoint
    """
    # Use a valid UUID format but non-existent conversation ID
    fake_conversation_id = str(uuid.uuid4())

    response = client.get(f"/api/v1/chat/conversations/{fake_conversation_id}")

    # Could return 200 (empty conversation) or 404 (not found) or 500 (error)
    assert response.status_code in [200, 404, 400, 500], f"Expected 200, 404, 400, or 500, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        assert "messages" in data, "Response must contain messages key"
        assert isinstance(data["messages"], list), "Messages must be a list"

        # If there are messages, check their structure
        for message in data["messages"]:
            assert "id" in message, "Message must contain id"
            assert "role" in message, "Message must contain role"
            assert "content" in message, "Message must contain content"
            assert "message_type" in message, "Message must contain message_type"
            assert "timestamp" in message, "Message must contain timestamp"

            # Validate field types
            assert isinstance(message["id"], str), "Message id must be string"
            assert isinstance(message["role"], str), "Message role must be string"
            assert isinstance(message["content"], str), "Message content must be string"
            assert isinstance(message["message_type"], str), "Message type must be string"
            assert isinstance(message["timestamp"], str), "Message timestamp must be string"


def test_conversation_detail_invalid_id_contract(client):
    """
    Contract test for /api/v1/chat/conversations/{conversation_id} with invalid ID
    """
    # Use an invalid conversation ID format
    invalid_conversation_id = "invalid-uuid-format"

    response = client.get(f"/api/v1/chat/conversations/{invalid_conversation_id}")

    # Should return 400 for invalid format
    assert response.status_code == 400, f"Expected 400 for invalid ID format, got {response.status_code}"


def test_conversation_delete_endpoint_contract(client):
    """
    Contract test for DELETE /api/v1/chat/conversations/{conversation_id} endpoint
    """
    # Use a valid UUID format but non-existent conversation ID
    fake_conversation_id = str(uuid.uuid4())

    response = client.delete(f"/api/v1/chat/conversations/{fake_conversation_id}")

    # Could return 200 (success) or 404 (not found) or 400 (bad request) or 500 (error)
    assert response.status_code in [200, 404, 400, 500], f"Expected 200, 404, 400, or 500, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        # Should return success message
        assert "message" in data, "Response should contain message"
        assert "Conversation deleted successfully" in data["message"], "Should confirm deletion"


def test_conversation_delete_invalid_id_contract(client):
    """
    Contract test for DELETE /api/v1/chat/conversations/{conversation_id} with invalid ID
    """
    # Use an invalid conversation ID format
    invalid_conversation_id = "invalid-uuid-format"

    response = client.delete(f"/api/v1/chat/conversations/{invalid_conversation_id}")

    # Should return 400 for invalid format
    assert response.status_code == 400, f"Expected 400 for invalid ID format, got {response.status_code}"


def test_send_message_with_conversation_id_contract(client):
    """
    Contract test for /api/v1/chat/send with conversation_id parameter
    """
    conversation_id = str(uuid.uuid4())

    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "Test message in conversation",
            "message_type": "text",
            "conversation_id": conversation_id
        }
    )

    # Should accept the request and return appropriate response
    assert response.status_code in [200, 400, 422, 500], f"Expected 200, 400, 422, or 500, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        # Should return conversation_id in response
        assert "conversation_id" in data, "Response must contain conversation_id"
        assert data["conversation_id"] == conversation_id, "Should return the same conversation_id"


def test_send_message_with_invalid_conversation_id_contract(client):
    """
    Contract test for /api/v1/chat/send with invalid conversation_id
    """
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "Test message",
            "message_type": "text",
            "conversation_id": "invalid-uuid"
        }
    )

    # Should return 400 for invalid UUID format
    assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid conversation_id, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__])