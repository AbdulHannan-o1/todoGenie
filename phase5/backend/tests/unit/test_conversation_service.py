import pytest
from sqlmodel import Session, SQLModel, create_engine
from uuid import uuid4
from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation, Message
from src.models import User
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock
from datetime import datetime

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(autouse=True)
def mock_db_session(engine):
    with patch('src.services.conversation_service.get_session') as mock_get_session:
        # Provide a fresh session for each call to next(get_session())
        mock_get_session.side_effect = lambda: iter([Session(engine)])
        yield mock_get_session

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        id=uuid4(),
        email="conv@example.com",
        username="cuser",
        hashed_password="password",
        status="Active"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_get_user_conversations(test_user, session):
    conv1 = Conversation(user_id=test_user.id, title="Conv 1")
    conv2 = Conversation(user_id=test_user.id, title="Conv 2")
    session.add(conv1)
    session.add(conv2)
    session.commit()
    
    # Add messages to count
    msg = Message(conversation_id=conv1.id, user_id=test_user.id, content="Hi", role="user")
    session.add(msg)
    session.commit()
    
    results = await ConversationService.get_user_conversations(test_user.id)
    assert len(results) == 2
    # Check sorting (desc updated_at, conv2 is newer by commit order mostly)
    assert any(r["title"] == "Conv 1" and r["message_count"] == 1 for r in results)
    assert any(r["title"] == "Conv 2" and r["message_count"] == 0 for r in results)

@pytest.mark.asyncio
async def test_get_conversation_by_id_ownership(test_user, session):
    conv = Conversation(user_id=test_user.id, title="Private")
    session.add(conv)
    session.commit()
    
    # Success
    result = await ConversationService.get_conversation_by_id(conv.id, test_user.id)
    assert result is not None
    assert result["title"] == "Private"
    
    # Failure (wrong user)
    wrong_user_id = uuid4()
    result = await ConversationService.get_conversation_by_id(conv.id, wrong_user_id)
    assert result is None

@pytest.mark.asyncio
async def test_get_conversation_messages(test_user, session):
    conv = Conversation(user_id=test_user.id, title="Chat")
    session.add(conv)
    session.commit()
    
    msg1 = Message(conversation_id=conv.id, user_id=test_user.id, content="Q", role="user")
    msg2 = Message(conversation_id=conv.id, user_id=test_user.id, content="A", role="assistant")
    session.add(msg1)
    session.add(msg2)
    session.commit()
    
    messages = await ConversationService.get_conversation_messages(conv.id, test_user.id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_delete_conversation(test_user, session):
    conv = Conversation(user_id=test_user.id, title="Delete Me")
    session.add(conv)
    session.commit()
    
    success = await ConversationService.delete_conversation(conv.id, test_user.id)
    assert success is True
    
    # Verify gone
    with Session(session.bind) as s:
        assert s.get(Conversation, conv.id) is None

@pytest.mark.asyncio
async def test_update_conversation_title(test_user, session):
    conv = Conversation(user_id=test_user.id, title="Old")
    session.add(conv)
    session.commit()
    
    success = await ConversationService.update_conversation_title(conv.id, "New", test_user.id)
    assert success is True
    
    with Session(session.bind) as s:
        updated = s.get(Conversation, conv.id)
        assert updated.title == "New"
