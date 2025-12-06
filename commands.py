from storage import storage
from spec import Task
from typing import List, Optional

def add_task(description: str) -> Task:
    """Adds a new task."""
    return storage.add_task(description)

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
