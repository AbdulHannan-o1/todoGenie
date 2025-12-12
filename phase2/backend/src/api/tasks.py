from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from backend.db import get_session
from backend.src.models.task import Task
from backend.src.schemas.task import TaskCreate, TaskUpdate, ReminderCreate
from backend.src.services.reminder_service import ReminderService
from backend.src.services.task_crud_service import TaskCRUDService
from backend.src.services.task_query_service import TaskQueryService
from backend.src.api.auth import get_current_user
from backend.src.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task.
    """
    task = Task.from_orm(task_create)
    task.user_id = current_user.id
    crud_service = TaskCRUDService(session)
    return crud_service.create_task(task)

@router.get("/", response_model=List[Task])
def list_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    search: Optional[str] = Query(None, description="Search tasks by title or description"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    status: Optional[str] = Query(None, description="Filter by status (pending, in progress, completed, archived, cancelled)"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: Optional[str] = Query("due_date", description="Sort by field (priority, due_date, alpha)"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc, desc)")
):
    """
    List all tasks for the current user, with optional filtering, searching, and sorting.
    """
    query_service = TaskQueryService(session)
    return query_service.query_tasks(
        user_id=current_user.id,
        search=search,
        priority=priority,
        status=status,
        tags=tags,
        sort_by=sort_by,
        sort_order=sort_order,
    )

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by its ID.
    """
    crud_service = TaskCRUDService(session)
    task = crud_service.get_task(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by its ID.
    """
    crud_service = TaskCRUDService(session)
    task = crud_service.get_task(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    updated_task = crud_service.update_task(task_id, task_update)
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by its ID.
    """
    crud_service = TaskCRUDService(session)
    task = crud_service.get_task(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if not crud_service.delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete task")

@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a specific task as complete.
    """
    crud_service = TaskCRUDService(session)
    task = crud_service.get_task(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task.status = "completed"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.post("/{task_id}/reminders", status_code=status.HTTP_201_CREATED)
def create_reminder(
    task_id: int,
    reminder_create: ReminderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a reminder for a specific task.
    """
    crud_service = TaskCRUDService(session)
    task = crud_service.get_task(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    reminder_service = ReminderService(session)
    reminder_service.create_reminder(task, reminder_create.reminder_date)
    return {"message": "Reminder created successfully"}
