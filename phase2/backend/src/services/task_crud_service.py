from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from ..models import Task
from ..schemas.task import TaskUpdate

class TaskCRUDService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        # Detach the object from the session to avoid relationship loading during serialization
        self.session.expunge(task)
        return task

    def get_task(self, task_id: UUID) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if task:
            # Detach the object from the session to avoid relationship loading during serialization
            self.session.expunge(task)
        return task

    def get_tasks(self, user_id: UUID) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = self.session.exec(statement).all()
        # Detach objects from the session to avoid relationship loading during serialization
        for task in tasks:
            self.session.expunge(task)
        return tasks

    def update_task(self, task_id: UUID, task_update: TaskUpdate) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        for key, value in task_update.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        # Detach the object from the session to avoid relationship loading during serialization
        self.session.expunge(task)
        return task

    def delete_task(self, task_id: UUID) -> bool:
        task = self.session.get(Task, task_id)
        if not task:
            return False
        self.session.delete(task)
        self.session.commit()
        return True
