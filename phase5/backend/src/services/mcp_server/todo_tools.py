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


class RecurrencePattern(BaseModel):
    frequency: str  # daily, weekly, monthly, yearly, custom
    interval: int = 1
    end_condition: Optional[Dict] = None  # {type: 'never', 'on_date', 'after_occurrences', value: date or count}


class TaskUpdateRequest(BaseModel):
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    reminder_time: Optional[str] = None
    tags: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    parent_task_id: Optional[str] = None


class TaskCompleteRequest(BaseModel):
    task_id: UUID
    completed: bool = True


def create_task_tool(title: str, description: Optional[str] = None, user_id: str = "",
                    tags: Optional[str] = None, priority: Optional[str] = None,
                    due_date: Optional[str] = None, reminder_time: Optional[str] = None,
                    recurrence_pattern: Optional[Dict] = None, parent_task_id: Optional[str] = None) -> Dict:
    """
    Create a new task via tool with optional tags, priority, due_date, reminders, recurrence, and hierarchical relationships
    """
    return TaskOperationsService.create_task(
        title, description, user_id, tags, priority, due_date,
        reminder_time, recurrence_pattern, parent_task_id
    )


def list_tasks_tool(user_id: str = "", include_completed: bool = True,
                   priority_filter: Optional[str] = None,
                   due_date_start: Optional[str] = None,
                   due_date_end: Optional[str] = None) -> List[Dict]:
    """
    List all tasks for a user via tool with optional filters
    """
    result = TaskOperationsService.list_tasks(
        user_id, include_completed, priority_filter, due_date_start, due_date_end
    )
    return result.get("tasks", [])


def update_task_tool(task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    due_date: Optional[str] = None,
                    reminder_time: Optional[str] = None,
                    tags: Optional[str] = None,
                    recurrence_pattern: Optional[Dict] = None,
                    parent_task_id: Optional[str] = None) -> Dict:
    """
    Update an existing task via tool with advanced features
    """
    return TaskOperationsService.update_task(
        task_id, title, description, status, priority, due_date,
        reminder_time, tags, recurrence_pattern, parent_task_id
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


def get_child_tasks_tool(task_id: str) -> List[Dict]:
    """
    Get all child tasks for a parent task
    """
    return TaskOperationsService.get_child_tasks(task_id)


def create_child_task_tool(parent_task_id: str, title: str, description: Optional[str] = None,
                          user_id: str = "", tags: Optional[str] = None,
                          priority: Optional[str] = None, due_date: Optional[str] = None,
                          reminder_time: Optional[str] = None,
                          recurrence_pattern: Optional[Dict] = None) -> Dict:
    """
    Create a child task under a parent task
    """
    return TaskOperationsService.create_child_task(
        parent_task_id, title, description, user_id, tags, priority,
        due_date, reminder_time, recurrence_pattern
    )


def get_upcoming_reminders_tool(user_id: str, hours_ahead: int = 24) -> List[Dict]:
    """
    Get upcoming reminders for a user
    """
    return TaskOperationsService.get_upcoming_reminders(user_id, hours_ahead)


def get_task_by_id_tool(task_id: str) -> Dict:
    """
    Get a specific task by ID
    """
    return TaskOperationsService.get_task_by_id(task_id)