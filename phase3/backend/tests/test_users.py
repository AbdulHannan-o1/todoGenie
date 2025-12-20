import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import app
from src.models import User, Task
from src.db.session import get_session



def test_create_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_create_user_existing_email(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpass"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_create_user_existing_username(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpass"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "another@example.com", "username": "testuser", "password": "anotherpass"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_create_user_invalid_email(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "invalid-email", "username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 422 # Unprocessable Entity for validation error

def test_create_user_short_password(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "short"},
    )
    assert response.status_code == 422 # Unprocessable Entity for validation error