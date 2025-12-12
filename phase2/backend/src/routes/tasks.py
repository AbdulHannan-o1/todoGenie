from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from backend.src.db.session import get_session
from backend.src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from backend.src.services import task_service

router = APIRouter()

@router.post("/tasks", response_model=TaskRead)
def create_task_endpoint(task_create: TaskCreate, session: Session = Depends(get_session)):
    # In a real application, user_id would come from authentication
    # For now, we'll assume task_create already has a user_id
    # Or we can hardcode it for testing purposes
    # task_create.user_id = 1 # Example hardcoded user_id
    
    db_task = task_service.create_task(session, task_create)
    return db_task

@router.get("/tasks", response_model=List[TaskRead])
def list_tasks_endpoint(
    user_id: int = Query(..., description="User ID to filter tasks"), # Assuming user_id comes from auth
    status: Optional[str] = Query(None, regex="^(pending|completed|in progress|archived)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    tags: Optional[List[str]] = Query(None),
    due_date_before: Optional[datetime] = None,
    due_date_after: Optional[datetime] = None,
    sort_by: Optional[str] = Query(None, regex="^(priority|due_date|title|created_at)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    session: Session = Depends(get_session)
):
    tasks = task_service.get_tasks(
        session=session,
        user_id=user_id,
        status=status,
        priority=priority,
        tags=tags,
        due_date_before=due_date_before,
        due_date_after=due_date_after,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task_endpoint(task_id: int, session: Session = Depends(get_session)):
    task = task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    # In a real application, user_id would come from authentication
    # and be used to verify ownership
    updated_task = task_service.update_task(session, task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task_endpoint(task_id: int, session: Session = Depends(get_session)):
    # In a real application, user_id would come from authentication
    # and be used to verify ownership
    deleted_task = task_service.delete_task(session, task_id)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return