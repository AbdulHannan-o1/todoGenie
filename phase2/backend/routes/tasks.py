from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import uuid

from models import Task, User
from db import get_session
from auth import get_current_user

router = APIRouter()

@router.post("/api/tasks", response_model=Task)
def create_task(task: Task, current_user_id: uuid.UUID = Depends(get_current_user), session: Session = Depends(get_session)):
    task.user_id = current_user_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/api/tasks", response_model=List[Task])
def get_tasks(current_user_id: uuid.UUID = Depends(get_current_user), session: Session = Depends(get_session)):
    tasks = session.exec(select(Task).where(Task.user_id == current_user_id)).all()
    return tasks

@router.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, current_user_id: uuid.UUID = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: Task, current_user_id: uuid.UUID = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task.title = task_update.title
    task.description = task_update.description
    task.completed = task_update.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user_id: uuid.UUID = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    session.delete(task)
    session.commit()
    return
