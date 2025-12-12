from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import or_
from backend.src.models.task import Task

class TaskQueryService:
    def __init__(self, session: Session):
        self.session = session

    def query_tasks(
        self,
        user_id: int,
        search: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[str] = "due_date",
        sort_order: Optional[str] = "asc"
    ) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id)

        if search:
            statement = statement.where(
                (Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))
            )

        if priority:
            statement = statement.where(Task.priority == priority)

        if status:
            statement = statement.where(Task.status == status)

        if tags:
            statement = statement.where(or_(*[Task.tags.like(f'%"{tag}"%') for tag in tags]))

        if sort_by == "priority":
            order_by = Task.priority.desc() if sort_order == "desc" else Task.priority.asc()
        elif sort_by == "due_date":
            order_by = Task.due_date.desc() if sort_order == "desc" else Task.due_date.asc()
        elif sort_by == "alpha":
            order_by = Task.title.desc() if sort_order == "desc" else Task.title.asc()
        else:
            order_by = Task.due_date.asc()

        statement = statement.order_by(order_by)

        return self.session.exec(statement).all()
