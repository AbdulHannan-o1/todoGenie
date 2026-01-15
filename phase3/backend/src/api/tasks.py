from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from ..db.session import get_session
from ..models import Task, User
from ..schemas.task import TaskCreate, TaskUpdate, ReminderCreate, TaskCreateRequest
from ..services.reminder_service import ReminderService
from ..services.task_crud_service import TaskCRUDService
from ..services.task_query_service import TaskQueryService
from .auth import get_current_user
from ..models import User

def create_tasks_router() -> APIRouter:
    router = APIRouter(prefix="/api", tags=["tasks"])

    @router.post("/{user_id}/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
    def create_task(
        user_id: UUID,
        task_create: TaskCreateRequest,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Create a new task for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create tasks for this user"
            )

        # Add user_id from the authenticated user
        task_data = task_create.model_dump()
        task_data['user_id'] = current_user.id  # Use authenticated user's ID
        task = Task(**task_data)
        crud_service = TaskCRUDService(session)
        created_task = crud_service.create_task(task)
        return created_task

    @router.get("/{user_id}/tasks", response_model=List[Task])
    def list_tasks(
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
        search: Optional[str] = Query(None, description="Search tasks by title or description"),
        priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
        status_: Optional[str] = Query(None, alias="status", description="Filter by status (pending, in progress, completed, archived, cancelled)"),
        tags: Optional[List[str]] = Query(None, description="Filter by tags"),
        sort_by: Optional[str] = Query("due_date", description="Sort by field (priority, due_date, alpha)"),
        sort_order: Optional[str] = Query("asc", description="Sort order (asc, desc)")
    ):
        """
        List all tasks for a specific user, with optional filtering, searching, and sorting.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view tasks for this user"
            )

        query_service = TaskQueryService(session)
        return query_service.query_tasks(
            user_id=current_user.id,
            search=search,
            priority=priority,
            status=status_,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    @router.get("/{user_id}/tasks/{task_id}", response_model=Task)
    def get_task(
        user_id: UUID,
        task_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Get a specific task by its ID for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view tasks for this user"
            )

        crud_service = TaskCRUDService(session)
        task = crud_service.get_task(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @router.put("/{user_id}/tasks/{task_id}", response_model=Task)
    def update_task(
        user_id: UUID,
        task_id: UUID,
        task_update: TaskUpdate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Update a specific task by its ID for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update tasks for this user"
            )

        crud_service = TaskCRUDService(session)
        task = crud_service.get_task(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        updated_task = crud_service.update_task(task_id, task_update)
        return updated_task

    @router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(
        user_id: UUID,
        task_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Delete a specific task by its ID for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete tasks for this user"
            )

        crud_service = TaskCRUDService(session)
        task = crud_service.get_task(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        if not crud_service.delete_task(task_id):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete task")

    @router.patch("/{user_id}/tasks/{task_id}/complete", response_model=Task)
    def complete_task(
        user_id: UUID,
        task_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Mark a specific task as complete for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update tasks for this user"
            )

        crud_service = TaskCRUDService(session)
        task = crud_service.get_task(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        task.status = "completed"
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @router.post("/{user_id}/tasks/{task_id}/reminders", status_code=status.HTTP_201_CREATED)
    def create_reminder(
        user_id: UUID,
        task_id: UUID,
        reminder_create: ReminderCreate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        """
        Create a reminder for a specific task for a specific user.
        """
        if str(current_user.id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create reminders for this user"
            )

        crud_service = TaskCRUDService(session)
        task = crud_service.get_task(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        reminder_service = ReminderService(session)
        reminder_service.create_reminder(task, reminder_create.reminder_date)
        return {"message": "Reminder created successfully"}

    return router

router = create_tasks_router()
