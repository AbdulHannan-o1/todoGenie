from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.db.session import get_session
from src.models import Task, TaskCreate, TaskUpdate, User, Notification
from src.auth import get_current_user
from src.services.recurring_tasks_service import RecurringTaskService
from src.services.reminder_service import ReminderService

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = Task(user_id=current_user.id, **task_create.dict())
    session.add(task)
    session.commit()
    session.refresh(task)

    # Handle recurring tasks and reminders
    if task.recurrence_pattern:
        # Additional logic could be added here for immediate processing
        pass

    if task.reminder_time:
        reminder_service = ReminderService(session)
        reminder_service.schedule_reminders_for_task(task)

    return task

@router.get("/", response_model=List[Task])
def read_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    # Get the original task attributes before updating
    original_reminder_time = task.reminder_time
    original_recurrence_pattern = task.recurrence_pattern

    task_data = task_update.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow() # Update timestamp

    session.add(task)
    session.commit()
    session.refresh(task)

    # Handle recurring tasks and reminders if anything changed
    if hasattr(task_update, 'reminder_time') and task_update.reminder_time is not None:
        # Cancel the old reminder if it existed
        if original_reminder_time:
            # In a full implementation, we would cancel the old reminder
            pass

        # Schedule the new reminder
        reminder_service = ReminderService(session)
        reminder_service.schedule_reminders_for_task(task)

    # If the task is completed and has a recurrence pattern, create the next instance
    if (hasattr(task_update, 'status') and task_update.status == 'completed' and
        task.recurrence_pattern):
        recurring_service = RecurringTaskService(session)
        recurring_service.process_completed_recurring_task(task.id)

    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    session.delete(task)
    session.commit()
    return {"ok": True}


@router.get("/reminders/upcoming", response_model=List[Notification])
def get_upcoming_reminders(
    hours_ahead: int = 24,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get upcoming reminders for the current user within the specified time window."""
    reminder_service = ReminderService(session)
    return reminder_service.get_upcoming_reminders(current_user.id, hours_ahead)


@router.get("/{task_id}/children", response_model=List[Task])
def get_task_children(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all child tasks for a parent task."""
    # Verify the parent task exists and belongs to the user
    parent_task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not parent_task:
        raise HTTPException(status_code=404, detail="Parent task not found or not owned by user")

    # Get all tasks that have this task as their parent
    children = session.exec(
        select(Task).where(Task.parent_task_id == task_id, Task.user_id == current_user.id)
    ).all()

    return children


@router.post("/{task_id}/children", response_model=Task)
def create_child_task(
    task_id: UUID,
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a child task under a parent task."""
    # Verify the parent task exists and belongs to the user
    parent_task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not parent_task:
        raise HTTPException(status_code=404, detail="Parent task not found or not owned by user")

    # Create the child task with the parent_task_id set
    child_task = Task(
        user_id=current_user.id,
        parent_task_id=task_id,
        title=task_create.title,
        description=task_create.description,
        status=getattr(task_create, 'status', 'pending'),
        priority=getattr(task_create, 'priority', 'medium'),
        recurrence_pattern=getattr(task_create, 'recurrence_pattern', None),
        due_date=getattr(task_create, 'due_date', None),
        reminder_time=getattr(task_create, 'reminder_time', None),
        tags=getattr(task_create, 'tags', ''),
        ai_generated=getattr(task_create, 'ai_generated', False),
        ai_intent=getattr(task_create, 'ai_intent', None),
        ai_context_id=getattr(task_create, 'ai_context_id', None)
    )

    session.add(child_task)
    session.commit()
    session.refresh(child_task)

    # Handle recurring tasks and reminders for the child
    if child_task.reminder_time:
        reminder_service = ReminderService(session)
        reminder_service.schedule_reminders_for_task(child_task)

    return child_task


@router.get("/{task_id}/ancestors", response_model=List[Task])
def get_task_ancestors(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all ancestor tasks for a child task (returns the parent and higher-level ancestors)."""
    # Verify the task exists and belongs to the user
    current_task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not current_task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    ancestors = []
    current_parent_id = current_task.parent_task_id

    # Traverse up the hierarchy to find all ancestors
    while current_parent_id:
        parent_task = session.exec(
            select(Task).where(Task.id == current_parent_id, Task.user_id == current_user.id)
        ).first()

        if parent_task:
            ancestors.append(parent_task)
            current_parent_id = parent_task.parent_task_id
        else:
            break  # Parent not found, stop traversal

    # Return ancestors in order from direct parent to top-level ancestor
    return list(reversed(ancestors))