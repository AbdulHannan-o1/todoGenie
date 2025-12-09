import pytest
from unittest.mock import Mock, patch
from src.commands import add_task, list_tasks, update_task, complete_task, delete_task
from src.models import Task, Priority

@pytest.fixture
def mock_storage():
    with patch('src.commands.storage') as mock_storage:
        yield mock_storage

@pytest.fixture
def sample_task():
    return Task(id=1, title="Test Task", description="Test Description", priority=Priority.MEDIUM, status="pending")

def test_add_task(mock_storage):
    mock_storage.add_task.return_value = Task(id=1, title="New Task", description="New Desc", priority=Priority.LOW)
    task = add_task("New Task", "New Desc", Priority.LOW)
    mock_storage.add_task.assert_called_once_with("New Task", "New Desc", Priority.LOW)
    assert task.title == "New Task"

def test_list_tasks(mock_storage, sample_task):
    mock_storage.get_all_tasks.return_value = [sample_task]
    tasks = list_tasks()
    mock_storage.get_all_tasks.assert_called_once()
    assert len(tasks) == 1
    assert tasks[0].id == 1

def test_update_task(mock_storage, sample_task):
    mock_storage.update_task.return_value = Task(id=1, title="Test Task", description="Updated Desc", priority=Priority.MEDIUM, status="pending")
    updated_task = update_task(1, "Updated Desc")
    mock_storage.update_task.assert_called_once_with(1, "Updated Desc")
    assert updated_task.description == "Updated Desc"

def test_complete_task(mock_storage, sample_task):
    mock_storage.complete_task.return_value = Task(id=1, title="Test Task", description="Test Description", priority=Priority.MEDIUM, status="completed")
    completed_task = complete_task(1)
    mock_storage.complete_task.assert_called_once_with(1)
    assert completed_task.status == "completed"

def test_delete_task(mock_storage):
    mock_storage.delete_task.return_value = True
    result = delete_task(1)
    mock_storage.delete_task.assert_called_once_with(1)
    assert result is True

def test_delete_task_not_found(mock_storage):
    mock_storage.delete_task.return_value = False
    result = delete_task(99)
    mock_storage.delete_task.assert_called_once_with(99)
    assert result is False
