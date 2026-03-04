import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID
import uuid
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, SQLModel, create_engine
from src.services.task_operations import TaskOperationsService
from src.models import Task, User

# Setup a test database engine
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def task_service():
    return TaskOperationsService()

@pytest.fixture
def test_user(engine):
    with Session(engine) as session:
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            status="Active"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@pytest.fixture(autouse=True)
def mock_db_session(engine):
    with patch('src.services.task_operations.get_session') as mock_get_session:
        # Provide a fresh session for each call to next(get_session())
        mock_get_session.side_effect = lambda: iter([Session(engine)])
        yield mock_get_session

def test_create_task_advanced(engine, task_service, test_user):
    user_id = str(test_user.id)
    title = "Advanced Task"
    description = "With all bells and whistles"
    priority = "high"
    tags = "work,urgent"
    due_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    
    result = task_service.create_task(
        title=title,
        description=description,
        user_id=user_id,
        priority=priority,
        tags=tags,
        due_date=due_date
    )
    
    assert result["status"] == "success"
    task_id = result["task_id"]
    
    # Verify in DB with a fresh session
    with Session(engine) as session:
        task = session.get(Task, UUID(task_id))
        assert task is not None
        assert task.title == title
        assert task.priority == priority
        assert task.tags == tags

def test_list_tasks_with_filters(engine, task_service, test_user):
    user_id = str(test_user.id)
    
    # Create some tasks
    with Session(engine) as session:
        t1 = Task(title="Task 1", user_id=test_user.id, priority="low", status="pending")
        t2 = Task(title="Task 2", user_id=test_user.id, priority="high", status="completed")
        session.add(t1)
        session.add(t2)
        session.commit()
    
    # Filter by priority
    result = task_service.list_tasks(user_id=user_id, priority_filter="high")
    assert len(result.get("tasks", [])) == 1
    assert result["tasks"][0]["title"] == "Task 2"
    
    # Filter completed
    result = task_service.list_tasks(user_id=user_id, include_completed=False)
    assert len(result.get("tasks", [])) == 1
    assert result["tasks"][0]["title"] == "Task 1"

def test_update_task_full(engine, task_service, test_user):
    with Session(engine) as session:
        task = Task(title="Old Title", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)
    
    result = task_service.update_task(
        task_id=task_id,
        title="New Title",
        status="completed",
        priority="medium"
    )
    
    assert result["status"] == "success"
    
    # Verify in DB
    with Session(engine) as session:
        db_task = session.get(Task, UUID(task_id))
        assert db_task.title == "New Title"
        assert db_task.status == "completed"
        assert db_task.priority == "medium"

def test_hierarchical_tasks(engine, task_service, test_user):
    user_id = str(test_user.id)
    
    # Create parent task
    with Session(engine) as session:
        parent = Task(title="Parent Task", user_id=test_user.id)
        session.add(parent)
        session.commit()
        session.refresh(parent)
        parent_id = str(parent.id)
    
    # Create child task
    result = task_service.create_child_task(
        parent_task_id=parent_id,
        title="Child Task",
        user_id=user_id
    )
    assert result["status"] == "success"
    child_id = result["task_id"]
    
    # Verify child relationship
    with Session(engine) as session:
        child_task = session.get(Task, UUID(child_id))
        assert str(child_task.parent_task_id) == parent_id
        # Get child tasks
        result = task_service.get_child_tasks(parent_id)
        assert result["status"] == "success"
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Child Task"

def test_delete_and_complete(engine, task_service, test_user):
    with Session(engine) as session:
        task = Task(title="To be changed", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)
    
    # Complete task
    task_service.complete_task(task_id, completed=True)
    
    with Session(engine) as session:
        db_task = session.get(Task, UUID(task_id))
        assert db_task.status == "completed"
    
    # Delete task
    result = task_service.delete_task(task_id)
    assert result["status"] == "success"
    
    with Session(engine) as session:
        assert session.get(Task, UUID(task_id)) is None

def test_upcoming_reminders(engine, task_service, test_user):
    user_id = str(test_user.id)
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    
    # Task with reminder in 1 hour
    with Session(engine) as session:
        t1 = Task(
            title="Recent Reminder",
            user_id=test_user.id,
            reminder_time=now + timedelta(hours=1),
            status="pending"
        )
        t2 = Task(
            title="Far Reminder",
            user_id=test_user.id,
            reminder_time=now + timedelta(hours=10),
            status="pending"
        )
        session.add(t1)
        session.add(t2)
        session.commit()
    
    # Get reminders in next 5 hours
    result = task_service.get_upcoming_reminders(user_id, hours_ahead=5)
    assert result["status"] == "success", result.get("message")
    assert len(result["reminders"]) == 1
    assert result["reminders"][0]["title"] == "Recent Reminder"

def test_get_task_by_id_success(engine, test_user):
    with Session(engine) as session:
        task = Task(title="Get Me", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)

    result = TaskOperationsService.get_task_by_id(task_id)
    assert result["status"] == "success"
    assert result["task"]["title"] == "Get Me"

def test_get_task_by_id_not_found(engine):
    task_id = str(uuid.uuid4())
    result = TaskOperationsService.get_task_by_id(task_id)
    assert result["status"] == "error"
    assert "not found" in result["message"]

def test_get_task_by_id_invalid_uuid():
    result = TaskOperationsService.get_task_by_id("not-a-uuid")
    assert result["status"] == "error"
    assert "Invalid task ID format" in result["message"]

def test_create_child_task_parent_not_found(engine, test_user):
    parent_id = str(uuid.uuid4())
    result = TaskOperationsService.create_child_task(
        parent_task_id=parent_id,
        title="Orphan Child",
        user_id=str(test_user.id)
    )
    assert result["status"] == "error"
    assert "not found" in result["message"]

def test_get_upcoming_reminders_invalid_uuid():
    result = TaskOperationsService.get_upcoming_reminders("bad-id")
    assert result["status"] == "error"
    assert "Invalid user ID format" in result["message"]

def test_delete_task_not_found(engine):
    task_id = str(uuid.uuid4())
    result = TaskOperationsService.delete_task(task_id)
    assert result["status"] == "error"
    assert "not found" in result["message"]

def test_update_task_not_found(engine):
    task_id = str(uuid.uuid4())
    result = TaskOperationsService.update_task(task_id, title="New Title")
    assert result["status"] == "error"
    assert "not found" in result["message"]
