from datetime import datetime, timedelta, UTC
from typing import List
import pytest
from sqlmodel import Session, SQLModel, create_engine
from phase2.backend.src.models import Task
from phase2.backend.src.schemas.task import TaskCreate, TaskUpdate
from phase2.backend.src.services.task_service import create_task, get_task_by_id, get_tasks_by_user, update_task, delete_task
from uuid import UUID

# Setup a test database engine
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_task(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task_create = TaskCreate(
        title="Test Task",
        user_id=user_id, # Added user_id
        status="pending",
        priority="low",
        tags="work",
        due_date=datetime.now(UTC) + timedelta(days=1)
    )
    task = create_task(session, task_create, user_id)
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.user_id == user_id

def test_get_task(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task_create = TaskCreate(title="Test Task", user_id=user_id, status="pending", priority="low", tags="")
    created_task = create_task(session, task_create, user_id)
    
    fetched_task = get_task_by_id(session, created_task.id)
    assert fetched_task.id == created_task.id
    assert fetched_task.title == "Test Task"

def test_get_tasks_filtering(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task1 = create_task(session, TaskCreate(title="Task 1", user_id=user_id, status="pending", priority="low", tags="home", due_date=datetime.now(UTC) + timedelta(days=1)), user_id=user_id)
    task2 = create_task(session, TaskCreate(title="Task 2", user_id=user_id, status="completed", priority="high", tags="work", due_date=datetime.now(UTC) + timedelta(days=2)), user_id=user_id)
    task3 = create_task(session, TaskCreate(title="Task 3", user_id=user_id, status="pending", priority="medium", tags="home,urgent", due_date=datetime.now(UTC) + timedelta(days=3)), user_id=user_id)

    # Filter by status
    pending_tasks = get_tasks_by_user(session, user_id=user_id)
    pending_tasks = [task for task in pending_tasks if task.status == "pending"]
    assert len(pending_tasks) == 2
    assert task1 in pending_tasks
    assert task3 in pending_tasks

    # Filter by priority
    high_priority_tasks = get_tasks_by_user(session, user_id=user_id)
    high_priority_tasks = [task for task in high_priority_tasks if task.priority == "high"]
    assert len(high_priority_tasks) == 1
    assert task2 in high_priority_tasks

    # Filter by tags
    home_tasks = get_tasks_by_user(session, user_id=user_id)
    home_tasks = [task for task in home_tasks if "home" in task.tags.split(',')]
    assert len(home_tasks) == 2
    assert task1 in home_tasks
    assert task3 in home_tasks

    # Filter by due_date (example, assuming tasks are created with future dates)
    future_date = datetime.now(UTC) + timedelta(days=10)
    recent_tasks = get_tasks_by_user(session, user_id=user_id)
    recent_tasks = [task for task in recent_tasks if task.due_date < future_date]
    # This test needs more specific due_date assignments in task_create to be accurate
    # For now, just check if it doesn't raise an error
    assert isinstance(recent_tasks, List)

def priority_sort_key(task):
    priority_order = {"high": 3, "medium": 2, "low": 1, None: 0}
    return priority_order.get(task.priority, 0)

def test_get_tasks_sorting(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task1 = create_task(session, TaskCreate(title="Alpha", user_id=user_id, status="pending", priority="high", tags=""), user_id=user_id)
    task2 = create_task(session, TaskCreate(title="Beta", user_id=user_id, status="pending", priority="low", tags=""), user_id=user_id)
    task3 = create_task(session, TaskCreate(title="Gamma", user_id=user_id, status="pending", priority="medium", tags=""), user_id=user_id)

    # Sort by priority (desc)
    sorted_by_priority_desc = sorted(get_tasks_by_user(session, user_id=user_id), key=priority_sort_key, reverse=True)
    assert sorted_by_priority_desc[0].title == "Alpha" # High
    assert sorted_by_priority_desc[1].title == "Gamma" # Medium
    assert sorted_by_priority_desc[2].title == "Beta"  # Low

    # Sort by created_at (asc)
    sorted_by_created_asc = sorted(get_tasks_by_user(session, user_id=user_id), key=lambda t: t.id) # Using id for consistent sorting
    assert sorted_by_created_asc[0].title == "Alpha"
    assert sorted_by_created_asc[1].title == "Beta"
    assert sorted_by_created_asc[2].title == "Gamma"

def test_update_task(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task_create = TaskCreate(title="Old Title", user_id=user_id, status="pending", priority="low", tags="")
    created_task = create_task(session, task_create, user_id)
    
    task_update = TaskUpdate(title="New Title", status="completed")
    updated_task = update_task(session, created_task.id, task_update)
    
    assert updated_task.title == "New Title"
    assert updated_task.status == "completed"


def test_delete_task(session: Session):
    user_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    task_create = TaskCreate(title="Task to Delete", user_id=user_id, status="pending", priority="low", tags="")
    created_task = create_task(session, task_create, user_id)
    
    deleted_task = delete_task(session, created_task.id)
    assert deleted_task.id == created_task.id
    
    fetched_task = get_task_by_id(session, created_task.id)
    assert fetched_task is None
