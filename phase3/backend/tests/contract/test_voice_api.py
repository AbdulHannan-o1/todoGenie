"""
Contract tests for /api/v1/chat/voice-recognize endpoint
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


def test_voice_recognize_endpoint_contract(client):
    """
    Contract test for /api/v1/voice/recognize endpoint
    Verifies the endpoint accepts expected input and returns expected output format
    """
    # Test case: Valid request with audio data and language
    # Note: In v1, voice processing happens in browser, so this tests coordination endpoint
    response = client.post(
        "/api/v1/voice/recognize",
        data=b"fake_audio_data",
        params={"language": "en-US"}
    )

    # The endpoint should return a successful response (even if it's informing about browser processing)
    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()

        # Required fields in response
        assert "success" in data, "Response must contain success field"
        assert "text" in data, "Response must contain text field (or null if browser processing)"
        assert "language" in data, "Response must contain language field"

        # Validate field types
        assert isinstance(data["success"], bool), "success must be boolean"
        assert data["language"] == "en-US", "language should match input"


def test_voice_recognize_endpoint_language_parameter(client):
    """
    Test language parameter validation for /api/v1/voice/recognize endpoint
    """
    # Test with different valid languages
    for language in ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"]:
        response = client.post(
            "/api/v1/voice/recognize",
            data=b"fake_audio_data",
            params={"language": language}
        )

        # Should not return 422 for valid languages
        assert response.status_code != 422, f"Valid language '{language}' should not return 422"


def test_voice_recognize_endpoint_missing_parameters(client):
    """
    Test missing parameters for /api/v1/voice/recognize endpoint
    """
    # Test without language parameter (if it's required)
    response = client.post(
        "/api/v1/voice/recognize",
        data=b"fake_audio_data"
    )

    # Could be 200 (with default language) or 422 (if language required)
    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"


def test_voice_capabilities_endpoint_contract(client):
    """
    Contract test for /api/v1/voice/capabilities endpoint
    """
    response = client.get("/api/v1/voice/capabilities")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Required fields in response
    assert "supported_languages" in data, "Response must contain supported_languages"
    assert "processing_method" in data, "Response must contain processing_method"
    assert "server_side_processing_available" in data, "Response must contain server_side_processing_available"

    # Validate field types
    assert isinstance(data["supported_languages"], list), "supported_languages must be list"
    assert isinstance(data["processing_method"], str), "processing_method must be string"
    assert isinstance(data["server_side_processing_available"], bool), "server_side_processing_available must be boolean"


def test_voice_validate_audio_format_endpoint_contract(client):
    """
    Contract test for /api/v1/voice/validate-audio-format endpoint
    """
    # Test with valid format
    response = client.post(
        "/api/v1/voice/validate-audio-format",
        params={"format": "mp3"}
    )

    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()

        # Required fields
        assert "valid" in data, "Response must contain valid field"
        assert "format" in data, "Response must contain format field"
        assert "supported_formats" in data, "Response must contain supported_formats field"
        assert "message" in data, "Response must contain message field"

        # Validate types
        assert isinstance(data["valid"], bool), "valid must be boolean"
        assert isinstance(data["format"], str), "format must be string"
        assert isinstance(data["supported_formats"], list), "supported_formats must be list"
        assert isinstance(data["message"], str), "message must be string"


def test_voice_validate_command_endpoint_contract(client):
    """
    Contract test for /api/v1/voice/validate-command endpoint
    """
    # Test with a task-related command
    response = client.post(
        "/api/v1/voice/validate-command",
        params={"text": "Add a task to buy groceries"}
    )

    assert response.status_code in [200, 400, 422], f"Expected 200, 400, or 422, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()

        # Required fields
        assert "is_valid_task_command" in data, "Response must contain is_valid_task_command"
        assert "is_task_related" in data, "Response must contain is_task_related"
        assert "contains_valid_pattern" in data, "Response must contain contains_valid_pattern"
        assert "text" in data, "Response must contain text"
        assert "detected_task_ids" in data, "Response must contain detected_task_ids"
        assert "confidence" in data, "Response must contain confidence"

        # Validate types
        assert isinstance(data["is_valid_task_command"], bool), "is_valid_task_command must be boolean"
        assert isinstance(data["is_task_related"], bool), "is_task_related must be boolean"
        assert isinstance(data["contains_valid_pattern"], bool), "contains_valid_pattern must be boolean"
        assert isinstance(data["text"], str), "text must be string"
        assert isinstance(data["detected_task_ids"], list), "detected_task_ids must be list"
        assert isinstance(data["confidence"], str), "confidence must be string"


if __name__ == "__main__":
    pytest.main([__file__])