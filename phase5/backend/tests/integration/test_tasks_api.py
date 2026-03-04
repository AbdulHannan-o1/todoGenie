import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from src.models import Task, User
from sqlmodel import Session, select

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client, test_user):
    # This assumes the conftest.py's client fixture doesn't handle auth automatically
    # or we need to provide the token. 
    # Actually, in this codebase, auth is usually mocked or uses a test token.
    # Looking at existing tests, they often use a specific header.
    return {"Authorization": f"Bearer test_token_{test_user.id}"}

def test_create_task_api(client, test_user):
    user_id = str(test_user.id)
    response = client.post(
        f"/api/v1/tasks/{user_id}/tasks",
        json={
            "title": "API Task",
            "description": "Created via API",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Task"
    assert data["user_id"] == user_id

def test_list_tasks_api(client, test_user, engine):
    user_id = str(test_user.id)
    # Seed data
    with Session(engine) as session:
        t1 = Task(title="T1", user_id=test_user.id, priority="low")
        t2 = Task(title="T2", user_id=test_user.id, priority="high")
        session.add(t1)
        session.add(t2)
        session.commit()

    # List all
    response = client.get(f"/api/v1/tasks/{user_id}/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 2

    # Filter by priority
    response = client.get(f"/api/v1/tasks/{user_id}/tasks?priority=high")
    assert response.status_code == 200
    tasks = response.json()
    assert all(t["priority"] == "high" for t in tasks)

def test_get_task_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        task = Task(title="Find Me", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    response = client.get(f"/api/v1/tasks/{user_id}/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find Me"

def test_update_task_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        task = Task(title="Old", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    response = client.put(
        f"/api/v1/tasks/{user_id}/tasks/{task_id}",
        json={"title": "New", "status": "in progress"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["status"] == "in progress"

def test_delete_task_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        task = Task(title="Dead", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    response = client.delete(f"/api/v1/tasks/{user_id}/tasks/{task_id}")
    assert response.status_code == 204

    # Verify gone
    with Session(engine) as session:
        assert session.get(Task, task.id) is None

def test_complete_task_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        task = Task(title="Soon to be done", user_id=test_user.id, status="pending")
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    response = client.patch(f"/api/v1/tasks/{user_id}/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_create_reminder_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        task = Task(title="Remind Me", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    reminder_date = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
    response = client.post(
        f"/api/v1/tasks/{user_id}/tasks/{task_id}/reminders",
        json={"reminder_date": reminder_date}
    )
    assert response.status_code == 201
    assert "success" in response.json()["message"].lower()

def test_hierarchy_api(client, test_user, engine):
    user_id = str(test_user.id)
    with Session(engine) as session:
        parent = Task(title="Parent", user_id=test_user.id)
        session.add(parent)
        session.commit()
        session.refresh(parent)
        parent_id = str(parent.id)

    # Create child
    response = client.post(
        f"/api/v1/tasks/{user_id}/tasks/{parent_id}/children",
        json={"title": "Child"}
    )
    assert response.status_code == 200
    child_id = response.json()["id"]
    assert response.json()["parent_task_id"] == parent_id

    # Get children
    response = client.get(f"/api/v1/tasks/{user_id}/tasks/{parent_id}/children")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == child_id

    # Get ancestors
    response = client.get(f"/api/v1/tasks/{user_id}/tasks/{child_id}/ancestors")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == parent_id

def test_tasks_api_unauthorized_access(client, test_user, engine):
    # Create another user
    with Session(engine) as session:
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            username="other",
            hashed_password="p"
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)
        other_user_id = str(other_user.id)

    # Try to access other user's tasks (as test_user)
    response = client.get(f"/api/v1/tasks/{other_user_id}/tasks")
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()
