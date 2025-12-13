import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from phase2.backend.src.main import app
from phase2.backend.src.models import User, Task
from phase2.backend.src.db.session import get_session
from phase2.backend.src.services.user_service import create_user
from phase2.backend.src.services.auth_service import create_user_access_token
from datetime import timedelta



@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, session: Session):
    user = create_user(session, "auth@example.com", "authuser", "authpass")
    access_token = create_user_access_token(user, timedelta(minutes=30))
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(name="another_auth_headers")
def another_auth_headers_fixture(client: TestClient, session: Session):
    user = create_user(session, "another@example.com", "anotheruser", "anotherpass")
    access_token = create_user_access_token(user, timedelta(minutes=30))
    return {"Authorization": f"Bearer {access_token}"}

def test_create_task(client: TestClient, auth_headers: dict):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Test Task", "status": "pending"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    assert "user_id" in data

def test_get_tasks(client: TestClient, auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task1 = Task(title="Task 1", user_id=user.id)
    task2 = Task(title="Task 2", user_id=user.id)
    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"

def test_get_single_task(client: TestClient, auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Single Task", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get(f"/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Task"
    assert data["id"] == str(task.id)

def test_get_single_task_unauthorized(client: TestClient, another_auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Unauthorized Task", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get(f"/tasks/{task.id}", headers=another_auth_headers)
    assert response.status_code == 404 # Or 403, depending on implementation
    assert response.json()["detail"] == "Task not found or not owned by user"

def test_update_task(client: TestClient, auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Original Task", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.put(
        f"/tasks/{task.id}",
        headers=auth_headers,
        json={"title": "Updated Task"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"

def test_update_task_unauthorized(client: TestClient, another_auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Unauthorized Update", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.put(
        f"/tasks/{task.id}",
        headers=another_auth_headers,
        json={"title": "Attempted Update"},
    )
    assert response.status_code == 404 # Or 403
    assert response.json()["detail"] == "Task not found or not owned by user"

def test_delete_task(client: TestClient, auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Task to Delete", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 204
    assert session.query(Task).filter(Task.id == task.id).first() is None

def test_delete_task_unauthorized(client: TestClient, another_auth_headers: dict, session: Session):
    user = session.query(User).filter(User.username == "authuser").first()
    task = Task(title="Unauthorized Delete", user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/tasks/{task.id}", headers=another_auth_headers)
    assert response.status_code == 404 # Or 403
    assert response.json()["detail"] == "Task not found or not owned by user"
