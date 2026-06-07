import pytest
from uuid import uuid4
from src.models import User, Conversation, Message
from sqlmodel import Session
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_send_message_api(client, test_user, engine):
    # Mock chatbot_service.process_user_message to avoid real LLM calls for this test
    # but still test the API layer
    with patch("src.api.v1.chat.chatbot_service.process_user_message", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {
            "success": True,
            "conversation_id": str(uuid4()),
            "response": "Hello world",
            "tool_results": []
        }
        
        response = client.post(
            "/api/v1/chat/send",
            json={"content": "Hi", "message_type": "text"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello world"
        assert data["message_type"] == "assistant"

@pytest.mark.asyncio
async def test_get_conversations_api(client, test_user, engine):
    with Session(engine) as session:
        c1 = Conversation(user_id=test_user.id, title="C1")
        session.add(c1)
        session.commit()
        
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(c["title"] == "C1" for c in response.json())

@pytest.mark.asyncio
async def test_get_conversation_history_api(client, test_user, engine):
    with Session(engine) as session:
        c1 = Conversation(user_id=test_user.id, title="C1")
        session.add(c1)
        session.commit()
        session.refresh(c1)
        
        m1 = Message(conversation_id=c1.id, user_id=test_user.id, content="Hi", role="user")
        session.add(m1)
        session.commit()
        
        conv_id = str(c1.id)

    response = client.get(f"/api/v1/chat/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "Hi"

@pytest.mark.asyncio
async def test_delete_conversation_api(client, test_user, engine):
    with Session(engine) as session:
        c1 = Conversation(user_id=test_user.id, title="To Delete")
        session.add(c1)
        session.commit()
        session.refresh(c1)
        conv_id = str(c1.id)

    response = client.delete(f"/api/v1/chat/conversations/{conv_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()

    # Verify gone
    with Session(engine) as session:
        assert session.get(Conversation, c1.id) is None

@pytest.mark.asyncio
async def test_chat_api_unauthorized(client, test_user, engine):
    # Try to delete a conversation that doesn't exist/belong to user
    fake_id = str(uuid4())
    response = client.delete(f"/api/v1/chat/conversations/{fake_id}")
    assert response.status_code == 404
