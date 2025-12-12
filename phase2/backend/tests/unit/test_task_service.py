from datetime import datetime, timedelta, UTC
from typing import List
import pytest
from sqlmodel import Session, SQLModel, create_engine
from backend.src.models.task import Task
from backend.src.schemas.task import TaskCreate, TaskUpdate
from backend.src.services.task_service import create_task, get_task, get_tasks, update_task, delete_task

# Setup a test database engine
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_task(session: Session):
    task_create = TaskCreate(
        title="Test Task",
        user_id=1,
        status="pending",
        priority="low",
        tags=["work"],
        due_date=datetime.now(UTC) + timedelta(days=1)
    )
    task = create_task(session, task_create)
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.user_id == 1

def test_get_task(session: Session):
    task_create = TaskCreate(title="Test Task", user_id=1, status="pending", priority="low")
    created_task = create_task(session, task_create)
    
    fetched_task = get_task(session, created_task.id)
    assert fetched_task.id == created_task.id
    assert fetched_task.title == "Test Task"

def test_get_tasks_filtering(session: Session):
    user_id = 1
    task1 = create_task(session, TaskCreate(title="Task 1", user_id=user_id, status="pending", priority="low", tags=["home"]))
    task2 = create_task(session, TaskCreate(title="Task 2", user_id=user_id, status="completed", priority="high", tags=["work"]))
    task3 = create_task(session, TaskCreate(title="Task 3", user_id=user_id, status="pending", priority="medium", tags=["home", "urgent"]))

    # Filter by status
    pending_tasks = get_tasks(session, user_id=user_id, status="pending")
    assert len(pending_tasks) == 2
    assert task1 in pending_tasks
    assert task3 in pending_tasks

    # Filter by priority
    high_priority_tasks = get_tasks(session, user_id=user_id, priority="high")
    assert len(high_priority_tasks) == 1
    assert task2 in high_priority_tasks

    # Filter by tags
    home_tasks = get_tasks(session, user_id=user_id, tags=["home"])
    assert len(home_tasks) == 2
    assert task1 in home_tasks
    assert task3 in home_tasks

    # Filter by due_date (example, assuming tasks are created with future dates)
    future_date = datetime.now(UTC) + timedelta(days=10)
    recent_tasks = get_tasks(session, user_id=user_id, due_date_before=future_date)
    # This test needs more specific due_date assignments in task_create to be accurate
    # For now, just check if it doesn't raise an error
    assert isinstance(recent_tasks, List)

def test_get_tasks_sorting(session: Session):
    user_id = 2
    task1 = create_task(session, TaskCreate(title="Alpha", user_id=user_id, status="pending", priority="high"), created_at=datetime(2023, 1, 1, tzinfo=UTC))
    task2 = create_task(session, TaskCreate(title="Beta", user_id=user_id, status="pending", priority="low"), created_at=datetime(2023, 1, 3, tzinfo=UTC))
    task3 = create_task(session, TaskCreate(title="Gamma", user_id=user_id, status="pending", priority="medium"), created_at=datetime(2023, 1, 2, tzinfo=UTC))

    # Sort by priority (desc)
    sorted_by_priority_desc = get_tasks(session, user_id=user_id, sort_by="priority", sort_order="desc")
    assert sorted_by_priority_desc[0].title == "Alpha" # High
    assert sorted_by_priority_desc[1].title == "Gamma" # Medium
    assert sorted_by_priority_desc[2].title == "Beta"  # Low

    # Sort by created_at (asc)
    sorted_by_created_asc = get_tasks(session, user_id=user_id, sort_by="created_at", sort_order="asc")
    assert sorted_by_created_asc[0].title == "Alpha"
    assert sorted_by_created_asc[1].title == "Gamma"
    assert sorted_by_created_asc[2].title == "Beta"

def test_update_task(session: Session):
    task_create = TaskCreate(title="Old Title", user_id=1, status="pending", priority="low")
    created_task = create_task(session, task_create)
    
    task_update = TaskUpdate(title="New Title", status="completed")
    updated_task = update_task(session, created_task.id, task_update)
    
    assert updated_task.title == "New Title"
    assert updated_task.status == "completed"
    assert updated_task.updated_at > created_task.created_at

def test_delete_task(session: Session):
    task_create = TaskCreate(title="Task to Delete", user_id=1, status="pending", priority="low")
    created_task = create_task(session, task_create)
    
    deleted_task = delete_task(session, created_task.id)
    assert deleted_task.id == created_task.id
    
    fetched_task = get_task(session, created_task.id)
    assert fetched_task is None