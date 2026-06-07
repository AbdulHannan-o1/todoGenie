from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session
from ..models import Task
from ..schemas.task import TaskCreate
import logging

logger = logging.getLogger(__name__)

def generate_recurring_task_instance(session: Session, original_task: Task) -> Optional[Task]:
    if not original_task.recurrence_pattern:
        return None

    try:
        import json

        # Extract recurrence type from the pattern if it exists
        recurrence_type = None
        if original_task.recurrence_pattern:
            if isinstance(original_task.recurrence_pattern, dict):
                recurrence_type = original_task.recurrence_pattern.get('type') or original_task.recurrence_pattern.get('recurrence')
            elif isinstance(original_task.recurrence_pattern, str):
                # Parse JSON string
                try:
                    pattern_dict = json.loads(original_task.recurrence_pattern)
                    recurrence_type = pattern_dict.get('type') or pattern_dict.get('recurrence')
                except json.JSONDecodeError:
                    # If JSON parsing fails, skip recurrence
                    return None

        new_due_date: Optional[datetime] = None
        if original_task.due_date and recurrence_type:
            if recurrence_type == "daily":
                new_due_date = original_task.due_date + timedelta(days=1)
            elif recurrence_type == "weekly":
                new_due_date = original_task.due_date + timedelta(weeks=1)
            elif recurrence_type == "monthly":
                # Simple monthly recurrence: add 30 days. More complex logic might be needed for exact month-end handling.
                new_due_date = original_task.due_date + timedelta(days=30)

        # Create a new task instance with status 'pending'
        # Note: TaskCreate doesn't have recurrence_pattern field, so we'll pass empty
        new_task_create = TaskCreate(
            title=original_task.title,
            description=original_task.description,
            user_id=original_task.user_id,
            status="pending",
            priority=original_task.priority,
            tags=original_task.tags,
            due_date=new_due_date
            # recurrence field not available in TaskCreate
        )
        
        # Create the new task but add the recurrence pattern manually since TaskCreate doesn't include it
        new_task = Task.model_validate(new_task_create)
        new_task.recurrence_pattern = original_task.recurrence_pattern  # Copy the recurrence pattern from original task
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        logger.info(f"Generated recurring instance for task: {original_task.id} for user: {original_task.user_id}")
        return new_task
    except Exception as e:
        logger.error(f"Error generating recurring instance for task {original_task.id}: {e}")
        raise