from datetime import datetime, UTC
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.models import Task, User
from src.schemas.task import TaskCreate, TaskUpdate
from uuid import UUID

def test_create_task_model():
    task = Task(
        title="Test Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
        status="pending",
        priority="low",
        tags="work",
        due_date=datetime.now(UTC)
    )
    assert task.title == "Test Task"
    assert task.user_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    assert task.status == "pending"
    assert task.priority == "low"
    assert "work" in task.tags

def test_task_create_schema():
    task_create = TaskCreate(
        title="New Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
        status="pending",
        priority="medium"
    )
    assert task_create.title == "New Task"
    assert task_create.user_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    assert task_create.status == "pending"
    assert task_create.priority == "medium"

def test_task_update_schema():
    task_update = TaskUpdate(
        title="Updated Task",
        status="completed"
    )
    assert task_update.title == "Updated Task"
    assert task_update.status == "completed"
    assert task_update.priority is None
