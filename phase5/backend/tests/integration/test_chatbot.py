import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
import json
from src.main import app
from src.api.dependencies import get_current_active_user
from src.models import User, Task
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from src.db.engine import set_test_engine

# Use the same database setup as unit tests
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    set_test_engine(engine) # Set as global engine
    return engine

@pytest.fixture(name="test_user")
def test_user_fixture(engine):
    with Session(engine) as session:
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="mocked_password",
            status="Active"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@pytest.fixture
def client(test_user, engine):
    """Create a test client with authenticated user and shared engine"""
    from src.db import get_session
    
    def override_get_session():
        with Session(engine) as session:
            yield session
            
    def mock_get_current_user():
        return test_user

    app.dependency_overrides[get_current_active_user] = mock_get_current_user
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    from src.db.engine import create_db_engine
    set_test_engine(create_db_engine()) # Reset after test

def test_text_based_todo_creation_full_flow(client, test_user, engine):
    """
    Integration test: Full flow from API to DB using real AI Agent logic (mocked provider)
    """
    mock_response_tool = MagicMock()
    mock_response_tool.choices = [MagicMock()]
    mock_message_tool = MagicMock()
    mock_message_tool.content = None
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "create_task"
    mock_tool_call.function.arguments = json.dumps({
        "title": "buy groceries",
        "priority": "high"
    })
    mock_message_tool.tool_calls = [mock_tool_call]
    mock_response_tool.choices[0].message = mock_message_tool

    mock_response_final = MagicMock()
    mock_response_final.choices = [MagicMock()]
    mock_message_final = MagicMock()
    mock_message_final.content = "I've added 'buy groceries' with high priority."
    mock_message_final.tool_calls = None
    mock_response_final.choices[0].message = mock_message_final

    with patch('src.services.ai_agent.main_service.AIAgentService.current_client') as mock_client:
        mock_client.chat.completions.create.side_effect = [mock_response_tool, mock_response_final]
        
        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Add a task to buy groceries with high priority",
                "message_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "buy groceries" in data["response"]
        
        # Verify Database
        with Session(engine) as session:
            tasks = session.exec(select(Task).where(Task.user_id == test_user.id)).all()
            assert len(tasks) == 1
            assert tasks[0].title == "buy groceries"
            assert tasks[0].priority == "high"

def test_text_based_todo_listing_full_flow(client, test_user, engine):
    """
    Integration test: Show tasks tool flow
    """
    # Pre-populate DB
    with Session(engine) as session:
        session.add(Task(title="Exist task", user_id=test_user.id))
        session.commit()
        
    mock_response_tool = MagicMock()
    mock_response_tool.choices = [MagicMock()]
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "list_tasks"
    mock_tool_call.function.arguments = json.dumps({})
    
    mock_msg = MagicMock()
    mock_msg.content = None
    mock_msg.tool_calls = [mock_tool_call]
    mock_response_tool.choices[0].message = mock_msg

    mock_response_final = MagicMock()
    mock_response_final.choices = [MagicMock()]
    mock_msg_final = MagicMock()
    mock_msg_final.content = "You have 1 task: Exist task"
    mock_msg_final.tool_calls = None
    mock_response_final.choices[0].message = mock_msg_final

    with patch('src.services.ai_agent.main_service.AIAgentService.current_client') as mock_client:
        mock_client.chat.completions.create.side_effect = [mock_response_tool, mock_response_final]
        
        response = client.post(
            "/api/v1/chat/send",
            json={"content": "Show my tasks"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Exist task" in data["response"]
        assert len(data["tool_results"]) > 0
        # tool_results[0] is the list of tasks returned by list_tasks_tool
        tasks = data["tool_results"][0]
        assert isinstance(tasks, list)
        assert any(t["title"] == "Exist task" for t in tasks)

def test_conversation_context_integration(client, test_user, engine):
    """
    Integration test: Verify conversation history is passed to AI Agent (chat_with_context path)
    """
    # 1. Create a conversation and an existing message
    from src.models.conversation import Conversation, Message
    with Session(engine) as session:
        conv = Conversation(user_id=test_user.id, title="Test Conversation")
        session.add(conv)
        session.commit()
        session.refresh(conv)
        
        msg = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            content="I need help with my taxes",
            role="user"
        )
        session.add(msg)
        
        reply = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            content="Sure, what about taxes?",
            role="assistant"
        )
        session.add(reply)
        session.commit()
        
        conv_id = conv.id

    # 2. Mock AI agent response for the new message
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Ok, I remember we were talking about taxes."
    mock_response.choices[0].message.tool_calls = None

    with patch('src.services.ai_agent.main_service.AIAgentService.current_client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        
        # 3. Send a new message in the same conversation
        response = client.post(
            "/api/v1/chat/send",
            json={
                "content": "Actually, let's add a task for it",
                "conversation_id": str(conv_id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "taxes" in data["response"]
        assert data["conversation_id"] == str(conv_id)
        
        # 4. Verify that the client was called with history
        # The history should should include the 2 previous messages + system message + new user message
        args, kwargs = mock_client.chat.completions.create.call_args
        messages = kwargs.get('messages', [])
        
        # System + History (User, Assistant) + Current User
        assert len(messages) >= 4
        assert any("taxes" in m["content"] for m in messages if m["role"] == "user")