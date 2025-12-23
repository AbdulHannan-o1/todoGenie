from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.db.session import get_session
from src.models import Task, TaskCreate, TaskUpdate
from auth_utils import get_current_user, TokenData

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(
    task_create: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = Task(user_id=UUID(current_user.user_id), **task_create.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=List[Task])
def read_tasks(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task).where(Task.user_id == UUID(current_user.user_id))).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == UUID(current_user.user_id))).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == UUID(current_user.user_id))).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    task_data = task_update.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow() # Update timestamp

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == UUID(current_user.user_id))).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    session.delete(task)
    session.commit()
    return {"ok": True}