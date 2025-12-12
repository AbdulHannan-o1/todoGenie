from typing import List, Optional
from sqlmodel import Session, select
from backend.src.models.task import Task

class TaskCRUDService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_tasks(self, user_id: int) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

    def update_task(self, task_id: int, task_update: Task) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        for key, value in task_update.dict(exclude_unset=True).items():
            setattr(task, key, value)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.session.get(Task, task_id)
        if not task:
            return False
        self.session.delete(task)
        self.session.commit()
        return True
