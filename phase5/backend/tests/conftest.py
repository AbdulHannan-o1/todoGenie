import pytest
import sys
import os
from typing import Generator
from sqlmodel import Session, SQLModel
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from unittest.mock import patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_ai_agent():
    """Globally mock the AI agent service to prevent real API calls unless TEST_REAL_AI is set"""
    if os.environ.get("TEST_REAL_AI") == "1":
        yield None, None
        return

    # Patch the class methods AND the instance in the chatbot service to be sure
    with patch('src.services.ai_agent.main_service.AIAgentService.process_message', new_callable=AsyncMock) as mock_class_process, \
         patch('src.services.ai_agent.main_service.AIAgentService.chat_with_context', new_callable=AsyncMock) as mock_class_chat, \
         patch('src.services.chatbot.ai_agent_service.process_message', new_callable=AsyncMock) as mock_inst_process, \
         patch('src.services.chatbot.ai_agent_service.chat_with_context', new_callable=AsyncMock) as mock_inst_chat:
        
        # Default successful response matching the expected structure
        default_response = {
            "success": True,
            "response": "I am a mocked AI assistant. How can I help you?",
            "tool_results": []
        }
        
        for mock in [mock_class_process, mock_class_chat, mock_inst_process, mock_inst_chat]:
            mock.return_value = default_response
        
        yield mock_class_process, mock_class_chat


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    from src.db.engine import create_db_engine
    from src.models import User, Task, Conversation, Message, Tag, TaskTag, Event, Notification

    # Create a fresh in-memory database engine for each test
    engine = create_db_engine("sqlite:///:memory:")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session without context manager to have manual control
    session = Session(engine)
    try:
        yield session
    finally:
        # Close the session and clean up
        try:
            session.close()
        except:
            pass  # Session might already be closed
        # Drop all tables after the test
        SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    # Import router creation functions inside the fixture to ensure proper initialization
    from src.api.auth import router as auth_router
    from src.api.users import router as users_router
    from src.api.tasks import router as tasks_router
    from src.api.v1.chat import router as chat_router
    from src.api.v1.voice import router as voice_router
    from src.db.session import get_session

    # Create a new FastAPI instance for testing
    test_app = FastAPI()

    # Add a custom middleware to handle session lifecycle properly
    @test_app.middleware("http")
    async def test_session_middleware(request: Request, call_next):
        # Store the original session state
        response = await call_next(request)
        # The service layer should handle its own commits/rollbacks
        # We just need to ensure the session is in a good state after the request
        return response

    # Create and include routers with the same prefixes as in main.py
    test_app.include_router(auth_router, prefix="/auth", tags=["auth"])
    test_app.include_router(users_router, prefix="/users", tags=["users"])
    test_app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
    test_app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    test_app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice"])

    # Add root route
    @test_app.get("/")
    def read_root():
        return {"message": "Hello World"}

    @test_app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Ensure session is cleaned up on exception
        try:
            session.rollback()
        except:
            pass  # Session might already be closed
            
        import traceback
        error_detail = f"Unexpected error: {str(exc)}\n{traceback.format_exc()}"
        print(error_detail) # Print to console for pytest -s
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": error_detail},
        )

    @test_app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Ensure session is cleaned up on HTTP exceptions
        try:
            session.rollback()
        except:
            pass  # Session might already be closed
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    def get_session_override():
        return session

    test_app.dependency_overrides[get_session] = get_session_override
    client = TestClient(test_app)
    # Store the app instance on the client for dependency overrides in tests
    client.app = test_app
    yield client
    # Clear overrides and ensure session is properly closed
    test_app.dependency_overrides.clear()


@pytest.fixture(name="auth_client")
def auth_client_fixture(client: TestClient, session: Session) -> TestClient:
    """Fixture that provides an authenticated client"""
    from src.api.dependencies import get_current_active_user
    from src.models import User
    import uuid

    user_uuid = uuid.uuid4()
    mock_user = User(
        id=user_uuid,
        email=f"test_{user_uuid.hex[:8]}@example.com",
        username=f"testuser_{user_uuid.hex[:8]}",
        hashed_password="$2b$12$examplehashedpassword",
        status="Active"
    )
    session.add(mock_user)
    session.commit()
    session.refresh(mock_user)

    # Override the authentication dependency on the app instance used by the client
    client.app.dependency_overrides[get_current_active_user] = lambda: mock_user
    yield client
    # Overrides are cleared by the client fixture's teardown