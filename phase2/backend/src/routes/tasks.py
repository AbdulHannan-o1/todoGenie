from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from phase2.backend.src.db.session import get_session
from phase2.backend.src.models import Task, User
from phase2.backend.src.services.task_service import create_task, get_task_by_id, get_tasks_by_user, update_task, delete_task, TaskCreate, TaskUpdate
from phase2.backend.src.auth import get_current_user

router = APIRouter()

@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return create_task(session, task_create, current_user.id)

@router.get("/tasks", response_model=List[Task])
def read_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return get_tasks_by_user(session, current_user.id)

@router.get("/tasks/{task_id}", response_model=Task)
def read_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = get_task_by_id(session, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")
    return task

@router.put("/tasks/{task_id}", response_model=Task)
def update_existing_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = update_task(session, task_id, task_update)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = get_task_by_id(session, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")
    delete_task(session, task_id)
    return