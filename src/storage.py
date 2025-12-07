from typing import List, Optional
from src.models import Task, Priority # Import Task and Priority from src.models

class TaskStorage:
    """Manages the in-memory storage of tasks."""
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1

    def add_task(self, title: str, description: str, priority: Priority) -> Task: # Modified signature
        """Adds a new task to the storage."""
        task = Task(id=self._next_id, title=title, description=description, priority=priority) # Updated Task instantiation
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Returns all tasks."""
        return self._tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Returns a task by its ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, new_description: str) -> Optional[Task]:
        """Updates a task's description."""
        task = self.get_task_by_id(task_id)
        if task:
            task.description = new_description
        return task

    def complete_task(self, task_id: int) -> Optional[Task]:
        """Marks a task as complete."""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = "completed" # Set status to completed
        return task

    def delete_task(self, task_id: int) -> bool:
        """Deletes a task."""
        task = self.get_task_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

storage = TaskStorage()
