from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session
from backend.src.models.task import Task
from backend.src.schemas.task import TaskCreate
import logging

logger = logging.getLogger(__name__)

def generate_recurring_task_instance(session: Session, original_task: Task) -> Optional[Task]:
    if not original_task.recurrence:
        return None

    try:
        new_due_date: Optional[datetime] = None
        if original_task.due_date:
            if original_task.recurrence == "daily":
                new_due_date = original_task.due_date + timedelta(days=1)
            elif original_task.recurrence == "weekly":
                new_due_date = original_task.due_date + timedelta(weeks=1)
            elif original_task.recurrence == "monthly":
                # Simple monthly recurrence: add 30 days. More complex logic might be needed for exact month-end handling.
                new_due_date = original_task.due_date + timedelta(days=30)
        
        # Create a new task instance with status 'pending'
        new_task_create = TaskCreate(
            title=original_task.title,
            description=original_task.description,
            user_id=original_task.user_id,
            status="pending",
            priority=original_task.priority,
            tags=original_task.tags,
            due_date=new_due_date,
            recurrence=original_task.recurrence
        )
        
        new_task = Task.model_validate(new_task_create)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        logger.info(f"Generated recurring instance for task: {original_task.id} for user: {original_task.user_id}")
        return new_task
    except Exception as e:
        logger.error(f"Error generating recurring instance for task {original_task.id}: {e}")
        raise