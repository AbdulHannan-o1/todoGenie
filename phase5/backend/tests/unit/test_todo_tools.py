import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID
import uuid
from src.services.mcp_server.todo_tools import (
    _find_tasks_by_criteria,
    complete_task_by_description,
    update_tasks_by_description,
    delete_tasks_by_description
)

@pytest.fixture
def mock_tasks():
    user_id = uuid.uuid4()
    return [
        {"id": str(uuid.uuid4()), "title": "Buy groceries", "description": "Milk and eggs", "status": "pending", "priority": "medium"},
        {"id": str(uuid.uuid4()), "title": "Call mom", "description": "Ask about weekend", "status": "pending", "priority": "high"},
        {"id": str(uuid.uuid4()), "title": "Finish report", "description": "Due tomorrow", "status": "completed", "priority": "urgent"},
    ], user_id

def test_find_tasks_by_criteria_exact(mock_tasks):
    tasks, user_id = mock_tasks
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        
        # Match by title
        result = _find_tasks_by_criteria(str(user_id), title="groceries")
        assert len(result) == 1
        assert result[0]["title"] == "Buy groceries"
        
        # Match by priority
        result = _find_tasks_by_criteria(str(user_id), priority="high")
        assert len(result) == 1
        assert result[0]["title"] == "Call mom"

def test_find_tasks_by_criteria_descriptions(mock_tasks):
    tasks, user_id = mock_tasks
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        
        # Match by text in description
        result = _find_tasks_by_criteria(str(user_id), title="weekend")
        assert len(result) == 1
        assert result[0]["title"] == "Call mom"

def test_complete_task_by_description_fuzzy(mock_tasks):
    tasks, user_id = mock_tasks
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        with patch('src.services.mcp_server.todo_tools.TaskOperationsService.complete_task') as mock_complete:
            mock_complete.return_value = {"status": "success"}
            
            # Fuzzy match "groceries" -> "Buy groceries"
            result = complete_task_by_description(title="grocries", user_id=str(user_id))
            assert result["status"] == "success"
            assert result["completed_tasks_count"] == 1
            mock_complete.assert_called_once()

def test_complete_task_by_description_ambiguous(mock_tasks):
    tasks, user_id = mock_tasks
    # Add another tasks that matches "buy"
    tasks.append({"id": str(uuid.uuid4()), "title": "Buy milk", "description": "", "status": "pending", "priority": "low"})
    
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        
        # "Buy" matches "Buy groceries" and "Buy milk"
        result = complete_task_by_description(title="Buy", user_id=str(user_id))
        assert result["status"] == "ambiguous"
        assert len(result["tasks"]) == 2

def test_update_tasks_by_description_single(mock_tasks):
    tasks, user_id = mock_tasks
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        with patch('src.services.mcp_server.todo_tools.TaskOperationsService.update_task') as mock_update:
            mock_update.return_value = {"status": "success"}
            
            result = update_tasks_by_description(
                title="groceries", 
                user_id=str(user_id),
                new_title="Buy organic groceries"
            )
            assert result["status"] == "success"
            mock_update.assert_called_once_with(
                task_id=tasks[0]["id"],
                title="Buy organic groceries",
                description=None,
                status=None,
                priority=None,
                due_date=None,
                reminder_time=None,
                tags=None,
                recurrence_pattern=None,
                parent_task_id=None
            )

def test_delete_tasks_by_description_fuzzy(mock_tasks):
    tasks, user_id = mock_tasks
    with patch('src.services.mcp_server.todo_tools.TaskOperationsService.list_tasks') as mock_list:
        mock_list.return_value = {"status": "success", "tasks": tasks}
        with patch('src.services.mcp_server.todo_tools.TaskOperationsService.delete_task') as mock_delete:
            mock_delete.return_value = {"status": "success"}
            
            # Fuzzy match "mom"
            result = delete_tasks_by_description(title="momm", user_id=str(user_id))
            assert result["status"] == "success"
            mock_delete.assert_called_once_with(tasks[1]["id"])
