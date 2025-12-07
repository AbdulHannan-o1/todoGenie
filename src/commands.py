from src.storage import storage
from src.models import Task, Priority # Import Priority
from typing import List, Optional
from rich.console import Console
from rich.text import Text

console = Console()

def add_task(title: str, description: str, priority: Priority) -> Task:
    """Adds a new task with title, description, and optional priority."""
    return storage.add_task(title, description, priority)

def list_tasks() -> List[Task]:
    """Lists all tasks."""
    return storage.get_all_tasks()

def update_task(task_id: int, new_description: str) -> Optional[Task]:
    """Updates a task's description."""
    return storage.update_task(task_id, new_description)

def complete_task(task_id: int) -> Optional[Task]:
    """Marks a task as complete."""
    return storage.complete_task(task_id)

def delete_task(task_id: int) -> bool:
    """Deletes a task."""
    return storage.delete_task(task_id)
