import pytest
import sys
import os
from typing import Generator
from sqlmodel import Session, SQLModel
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import your models here to ensure they are registered with SQLModel.metadata
from src.models import User, Task
from src.db.session import get_session
from src.db.engine import create_db_engine, set_test_engine # Import create_db_engine and set_test_engine

# Import router creation functions
from src.api.auth import create_auth_router
from src.api.tasks import create_tasks_router

@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    test_engine = create_db_engine("sqlite:///:memory:") # Use the new function to create the test engine
    set_test_engine(test_engine) # Set the global engine in engine.py
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    # Create a new FastAPI instance for testing
    test_app = FastAPI()
    
    # Create and include routers
    test_app.include_router(create_auth_router())
    test_app.include_router(create_tasks_router())

    # Add root route
    @test_app.get("/")
    def read_root():
        return {"message": "Hello World"}

    # Add exception handlers
    @test_app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )

    @test_app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    def get_session_override():
        return session

    test_app.dependency_overrides[get_session] = get_session_override
    client = TestClient(test_app)
    yield client
    test_app.dependency_overrides.clear()

