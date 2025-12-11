from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, asc, desc
from sqlalchemy import case # Added this line
from phase2.backend.src.models.task import Task, TaskCreate, TaskUpdate
from phase2.backend.src.services.recurrence_service import generate_recurring_task_instance # Added this line
import logging

logger = logging.getLogger(__name__)

def create_task(session: Session, task_create: TaskCreate, created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None) -> Task:
    try:
        task_data = task_create.model_dump()
        if created_at:
            task_data["created_at"] = created_at
        if updated_at:
            task_data["updated_at"] = updated_at
        
        task = Task(**task_data) # Create Task object from dictionary
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task created: {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise

def get_task(session: Session, task_id: int) -> Optional[Task]:
    try:
        task = session.get(Task, task_id)
        if task:
            logger.info(f"Task fetched: {task.id}")
        else:
            logger.warning(f"Task not found: {task_id}")
        return task
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise

def get_tasks(
    session: Session, 
    user_id: int, 
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date_before: Optional[datetime] = None,
    due_date_after: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
) -> List[Task]:
    try:
        statement = select(Task).where(Task.user_id == user_id)

        if status:
            statement = statement.where(Task.status == status)
        if priority:
            statement = statement.where(Task.priority == priority)
        if tags:
            for tag in tags:
                statement = statement.where(Task.tags.contains(tag)) # This might need adjustment for array contains
        if due_date_before:
            statement = statement.where(Task.due_date < due_date_before)
        if due_date_after:
            statement = statement.where(Task.due_date > due_date_after)

        if sort_by:
            if sort_by == "priority":
                # Custom sorting for priority enum
                if sort_order == "asc":
                    statement = statement.order_by(
                        case(
                            (Task.priority == "high", 1),
                            (Task.priority == "medium", 2),
                            (Task.priority == "low", 3),
                            else_=4
                        )
                    )
                else:
                    statement = statement.order_by(
                        case(
                            (Task.priority == "low", 1),
                            (Task.priority == "medium", 2),
                            (Task.priority == "high", 3),
                            else_=4
                        ).desc()
                    )
            elif hasattr(Task, sort_by):
                if sort_order == "asc":
                    statement = statement.order_by(asc(getattr(Task, sort_by)))
                else:
                    statement = statement.order_by(desc(getattr(Task, sort_by)))
        
        tasks = session.exec(statement).all()
        logger.info(f"Fetched {len(tasks)} tasks for user {user_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks for user {user_id}: {e}")
        raise

def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    try:
        task = session.get(Task, task_id)
        if not task:
            logger.warning(f"Task not found for update: {task_id}")
            return None
        
        # Store old status to check for completion
        old_status = task.status

        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task updated: {task.id}")

        # Check if task was completed and has recurrence
        if old_status != "completed" and task.status == "completed" and task.recurrence:
            generate_recurring_task_instance(session, task)
            logger.info(f"Generated recurring instance for task: {task.id}")

        return task
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise

def delete_task(session: Session, task_id: int) -> Optional[Task]:
    try:
        task = session.get(Task, task_id)
        if not task:
            logger.warning(f"Task not found for deletion: {task_id}")
            return None
        session.delete(task)
        session.commit()
        logger.info(f"Task deleted: {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise