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
    from src.api.auth import create_auth_router
    from src.api.tasks import create_tasks_router
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
    test_app.include_router(create_auth_router(), prefix="/auth")
    test_app.include_router(create_tasks_router(), prefix="/tasks")

    # Add root route
    @test_app.get("/")
    def read_root():
        return {"message": "Hello World"}

    # Add exception handlers
    @test_app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Ensure session is cleaned up on exception
        try:
            session.rollback()
        except:
            pass  # Session might already be closed
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
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
    yield client
    # Clear overrides and ensure session is properly closed
    test_app.dependency_overrides.clear()