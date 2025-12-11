from datetime import datetime, UTC
from phase2.backend.src.models.task import Task, TaskCreate, TaskUpdate

def test_create_task_model():
    task = Task(
        title="Test Task",
        user_id=1,
        status="pending",
        priority="low",
        tags=["work"],
        due_date=datetime.now(UTC)
    )
    assert task.title == "Test Task"
    assert task.user_id == 1
    assert task.status == "pending"
    assert task.priority == "low"
    assert "work" in task.tags

def test_task_create_schema():
    task_create = TaskCreate(
        title="New Task",
        user_id=1,
        status="pending",
        priority="medium"
    )
    assert task_create.title == "New Task"
    assert task_create.user_id == 1

def test_task_update_schema():
    task_update = TaskUpdate(
        title="Updated Task",
        status="completed"
    )
    assert task_update.title == "Updated Task"
    assert task_update.status == "completed"
    assert task_update.priority is None