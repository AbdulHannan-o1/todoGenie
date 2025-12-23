from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session
from phase2.backend.src.models import Task
from phase2.backend.src.services.task_crud_service import TaskCRUDService

class TaskSchedulingService:
    def __init__(self, session: Session):
        self.session = session
        self.crud_service = TaskCRUDService(session)

    def create_recurring_tasks(self, task: Task) -> List[Task]:
        if not task.recurrence or not task.due_date:
            return []

        new_tasks = []
        if task.recurrence == "daily":
            delta = timedelta(days=1)
        elif task.recurrence == "weekly":
            delta = timedelta(weeks=1)
        elif task.recurrence == "monthly":
            # This is a simplified implementation for monthly recurrence
            delta = timedelta(days=30)
        else:
            return []

        # Create 5 recurring tasks for now
        for i in range(1, 6):
            new_due_date = task.due_date + (delta * i)
            new_task = Task(
                title=task.title,
                description=task.description,
                status="pending",
                priority=task.priority,
                tags=task.tags,
                due_date=new_due_date,
                recurrence=task.recurrence,
                user_id=task.user_id
            )
            new_tasks.append(self.crud_service.create_task(new_task))

        return new_tasks
