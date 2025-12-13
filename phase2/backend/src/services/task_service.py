from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from phase2.backend.src.db.session import get_session
from phase2.backend.src.models import Task, User
from phase2.backend.src.schemas.task import TaskCreate, TaskUpdate
from phase2.backend.src.services.task_crud_service import TaskCRUDService
from phase2.backend.src.services.task_query_service import TaskQueryService


def create_task(session: Session, task_create: TaskCreate, user_id: UUID) -> Task:
    task = Task.model_validate(task_create, update={"user_id": user_id})
    crud_service = TaskCRUDService(session)
    return crud_service.create_task(task)

def get_task_by_id(session: Session, task_id: UUID) -> Optional[Task]:
    crud_service = TaskCRUDService(session)
    return crud_service.get_task(task_id)

def get_tasks_by_user(session: Session, user_id: UUID) -> List[Task]:
    query_service = TaskQueryService(session)
    return query_service.query_tasks(user_id=user_id)

def update_task(session: Session, task_id: UUID, task_update: TaskUpdate) -> Optional[Task]:
    crud_service = TaskCRUDService(session)
    return crud_service.update_task(task_id, task_update)

def delete_task(session: Session, task_id: UUID) -> bool:
    crud_service = TaskCRUDService(session)
    return crud_service.delete_task(task_id)
