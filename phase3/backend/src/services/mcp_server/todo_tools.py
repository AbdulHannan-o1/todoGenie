"""
MCP tools for todo operations that can be called by the AI agent
"""
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
import aiomcp
from src.services.task_operations import TaskOperationsService


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID


class TaskUpdateRequest(BaseModel):
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


class TaskCompleteRequest(BaseModel):
    task_id: UUID
    completed: bool = True


def create_task_tool(title: str, description: Optional[str] = None, user_id: str = "") -> Dict:
    """
    Create a new task via tool
    """
    return TaskOperationsService.create_task(title, description, user_id)


def list_tasks_tool(user_id: str = "") -> List[Dict]:
    """
    List all tasks for a user via tool
    """
    result = TaskOperationsService.list_tasks(user_id)
    return result.get("tasks", [])


def update_task_tool(task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    due_date: Optional[str] = None) -> Dict:
    """
    Update an existing task via tool
    """
    return TaskOperationsService.update_task(
        task_id, title, description, status, priority, due_date
    )


def delete_task_tool(task_id: str) -> Dict:
    """
    Delete a task via tool
    """
    return TaskOperationsService.delete_task(task_id)


def complete_task_tool(task_id: str, completed: bool = True) -> Dict:
    """
    Mark a task as complete/incomplete via tool
    """
    return TaskOperationsService.complete_task(task_id, completed)