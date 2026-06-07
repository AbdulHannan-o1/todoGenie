from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.db.session import get_session
from src.models import Tag, User, Task
from src.auth import get_current_user
from src.services.tags_service import TagsService


router = APIRouter()


@router.post("/", response_model=Tag)
def create_tag(
    tag_data: Tag,  # Using Pydantic model for input validation
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tags_service = TagsService(session)

    # Create the tag with the current user's ID
    tag = tags_service.create_tag(
        user_id=current_user.id,
        name=tag_data.name,
        color=getattr(tag_data, 'color', None)
    )
    return tag


@router.get("/", response_model=List[Tag])
def read_tags(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tags_service = TagsService(session)
    tags = tags_service.get_user_tags(user_id=current_user.id)
    return tags


@router.get("/{tag_id}", response_model=Tag)
def read_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tags_service = TagsService(session)
    tag = tags_service.get_tag_by_id(tag_id=tag_id, user_id=current_user.id)

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found or not owned by user")

    return tag


@router.put("/{tag_id}", response_model=Tag)
def update_tag(
    tag_id: UUID,
    tag_update: Tag,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tags_service = TagsService(session)

    updated_tag = tags_service.update_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        name=getattr(tag_update, 'name', None),
        color=getattr(tag_update, 'color', None)
    )

    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found or not owned by user")

    return updated_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tags_service = TagsService(session)
    success = tags_service.delete_tag(tag_id=tag_id, user_id=current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Tag not found or not owned by user")

    return {"ok": True}


@router.post("/assign/{task_id}/{tag_id}")
def assign_tag_to_task(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify that the task belongs to the user
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    tags_service = TagsService(session)
    success = tags_service.assign_tag_to_task(task_id=task_id, tag_id=tag_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign tag to task")

    return {"message": "Tag assigned to task successfully"}


@router.post("/remove/{task_id}/{tag_id}")
def remove_tag_from_task(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify that the task belongs to the user
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    tags_service = TagsService(session)
    success = tags_service.remove_tag_from_task(task_id=task_id, tag_id=tag_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove tag from task")

    return {"message": "Tag removed from task successfully"}


@router.get("/task/{task_id}", response_model=List[Tag])
def get_tags_for_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify that the task belongs to the user
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    tags_service = TagsService(session)
    tags = tags_service.get_tags_for_task(task_id=task_id)
    return tags