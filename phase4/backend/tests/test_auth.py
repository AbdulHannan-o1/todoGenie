import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import app
from src.models import User
from src.db.session import get_session
from src.services.user_service import create_user
from src.utils.hash import get_password_hash



def test_login_success(client: TestClient, session: Session):
    # Register a user first
    create_user(
        session=session,
        email="test@example.com",
        username="testuser",
        password="testpass"
    )

    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "testpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_invalid_password(client: TestClient, session: Session):
    # Register a user first
    create_user(
        session=session,
        email="test@example.com",
        username="testuser",
        password="testpass"
    )

    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_failure_user_not_found(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent@example.com", "password": "anypass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_with_username_success(client: TestClient, session: Session):
    # Register a user first
    create_user(
        session=session,
        email="test@example.com",
        username="testuser",
        password="testpass"
    )

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_invalid_identifier_format(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "invalid-identifier", "password": "testpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"