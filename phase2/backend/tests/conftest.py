import pytest
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
import os

# Import your models here to ensure they are registered with SQLModel.metadata
from backend.src.models.user import User
from backend.src.models.task import Task

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    SQLModel.metadata.create_all(engine)  # Create tables
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)  # Drop tables after tests

@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    from backend.src.main import app
    from backend.db import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
