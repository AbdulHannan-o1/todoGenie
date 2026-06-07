from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID

from ..models import Tag, TaskTag, User
from ..db.session import get_session


class TagsService:
    """
    Service for handling tags functionality.
    Manages creation, assignment, and retrieval of tags.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_tag(self, user_id: UUID, name: str, color: Optional[str] = None) -> Tag:
        """
        Creates a new tag for a user.

        Args:
            user_id: The ID of the user creating the tag
            name: The name of the tag
            color: Optional color for the tag

        Returns:
            The created Tag object
        """
        tag = Tag(
            user_id=user_id,
            name=name,
            color=color
        )

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    def get_user_tags(self, user_id: UUID) -> List[Tag]:
        """
        Gets all tags for a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of tags belonging to the user
        """
        statement = select(Tag).where(Tag.user_id == user_id)
        return self.session.exec(statement).all()

    def get_tag_by_id(self, tag_id: UUID, user_id: UUID) -> Optional[Tag]:
        """
        Gets a specific tag by ID for a user.

        Args:
            tag_id: The ID of the tag
            user_id: The ID of the user

        Returns:
            The tag if it belongs to the user, None otherwise
        """
        statement = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        return self.session.exec(statement).first()

    def update_tag(self, tag_id: UUID, user_id: UUID, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Tag]:
        """
        Updates a tag for a user.

        Args:
            tag_id: The ID of the tag
            user_id: The ID of the user
            name: New name for the tag (optional)
            color: New color for the tag (optional)

        Returns:
            Updated tag if successful, None if tag doesn't exist or doesn't belong to user
        """
        tag = self.get_tag_by_id(tag_id, user_id)
        if not tag:
            return None

        if name is not None:
            tag.name = name
        if color is not None:
            tag.color = color

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    def delete_tag(self, tag_id: UUID, user_id: UUID) -> bool:
        """
        Deletes a tag for a user.

        Args:
            tag_id: The ID of the tag
            user_id: The ID of the user

        Returns:
            True if deletion was successful, False otherwise
        """
        tag = self.get_tag_by_id(tag_id, user_id)
        if not tag:
            return False

        self.session.delete(tag)
        self.session.commit()
        return True

    def assign_tag_to_task(self, task_id: UUID, tag_id: UUID) -> bool:
        """
        Assigns a tag to a task.

        Args:
            task_id: The ID of the task
            tag_id: The ID of the tag

        Returns:
            True if assignment was successful, False otherwise
        """
        # Check if the relationship already exists
        statement = select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        )
        existing = self.session.exec(statement).first()

        if existing:
            return True  # Already assigned

        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        self.session.add(task_tag)
        self.session.commit()

        return True

    def remove_tag_from_task(self, task_id: UUID, tag_id: UUID) -> bool:
        """
        Removes a tag from a task.

        Args:
            task_id: The ID of the task
            tag_id: The ID of the tag

        Returns:
            True if removal was successful, False otherwise
        """
        statement = select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        )
        task_tag = self.session.exec(statement).first()

        if not task_tag:
            return False  # Relationship doesn't exist

        self.session.delete(task_tag)
        self.session.commit()
        return True

    def get_tags_for_task(self, task_id: UUID) -> List[Tag]:
        """
        Gets all tags associated with a task.

        Args:
            task_id: The ID of the task

        Returns:
            List of tags associated with the task
        """
        statement = select(Tag).join(TaskTag).where(TaskTag.task_id == task_id)
        return self.session.exec(statement).all()

    def get_tasks_for_tag(self, tag_id: UUID, user_id: UUID) -> List:
        """
        Gets all tasks associated with a tag for a user.

        Args:
            tag_id: The ID of the tag
            user_id: The ID of the user

        Returns:
            List of tasks associated with the tag
        """
        from ..models import Task  # Import here to avoid circular imports
        statement = select(Task).join(TaskTag).where(
            TaskTag.tag_id == tag_id,
            Task.user_id == user_id
        )
        return self.session.exec(statement).all()