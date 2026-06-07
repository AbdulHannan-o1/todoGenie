"""
Contract tests for /api/v1/chat/send endpoint
"""
import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is in main.py
from auth import get_current_user
from models import User
import uuid


@pytest.fixture
def client():
    """Create a test client with authenticated user"""
    with TestClient(app) as test_client:
        # Mock the authentication dependency
        def mock_get_current_user():
            # Create a mock user with required attributes
            mock_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                name="Test User",
                password="hashed_password"  # This would be properly hashed in real scenario
            )
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        yield test_client
        app.dependency_overrides.clear()


def test_chat_send_endpoint_contract(client):
    """
    Contract test for /api/v1/chat/send endpoint
    Verifies the endpoint accepts expected input and returns expected output format
    """
    # Test case 1: Valid request with text message
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "Add a task to buy groceries",
            "message_type": "text"
        }
    )

    # Assert response status
    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"

    # If successful, check response structure
    if response.status_code == 200:
        data = response.json()

        # Required fields in response
        assert "conversation_id" in data, "Response must contain conversation_id"
        assert "response" in data, "Response must contain response message"
        assert "tool_results" in data, "Response must contain tool_results"
        assert "message_type" in data, "Response must contain message_type"

        # Validate field types
        assert isinstance(data["conversation_id"], (str, type(None))), "conversation_id must be string or None"
        assert isinstance(data["response"], str), "response must be string"
        assert isinstance(data["tool_results"], list), "tool_results must be list"
        assert data["message_type"] == "assistant", "message_type should be 'assistant'"

    # Test case 2: Request with voice message type
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "Show my tasks",
            "message_type": "voice"
        }
    )

    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"

    # Test case 3: Missing required fields (should return 422 or 400)
    response = client.post(
        "/api/v1/chat/send",
        json={}  # Missing required fields
    )

    assert response.status_code in [400, 422], f"Expected 400 or 422 for missing fields, got {response.status_code}"

    # Test case 4: Invalid message_type
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "Test message",
            "message_type": "invalid_type"
        }
    )

    assert response.status_code == 400, f"Expected 400 for invalid message_type, got {response.status_code}"


def test_chat_send_endpoint_content_validation(client):
    """
    Test content validation for /api/v1/chat/send endpoint
    """
    # Test case: Empty content should return 400
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "",
            "message_type": "text"
        }
    )

    assert response.status_code == 400, f"Expected 400 for empty content, got {response.status_code}"

    # Test case: Whitespace-only content should return 400
    response = client.post(
        "/api/v1/chat/send",
        json={
            "content": "   ",
            "message_type": "text"
        }
    )

    assert response.status_code == 400, f"Expected 400 for whitespace-only content, got {response.status_code}"


def test_chat_send_endpoint_message_type_validation(client):
    """
    Test message_type validation for /api/v1/chat/send endpoint
    """
    # Test case: Valid message types
    for valid_type in ["text", "voice"]:
        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Test message",
                "message_type": valid_type
            }
        )

        # Should not return 400 for valid types (could be 200 or 500 depending on other processing)
        assert response.status_code != 400, f"Valid message_type '{valid_type}' should not return 400"


if __name__ == "__main__":
    pytest.main([__file__])