from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID

from ..models import Task
from ..db.session import get_session


class TaskHierarchyService:
    """
    Service for handling hierarchical task operations.
    Manages parent-child relationships between tasks.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_task_with_hierarchy(self, task_id: UUID, user_id: UUID) -> Optional[dict]:
        """
        Gets a task with its parent and children information.

        Args:
            task_id: The ID of the task
            user_id: The ID of the user

        Returns:
            Dictionary containing the task and its hierarchical information
        """
        # Get the task
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return None

        # Get children
        children = self.session.exec(
            select(Task).where(Task.parent_task_id == task_id, Task.user_id == user_id)
        ).all()

        # Get parent
        parent = None
        if task.parent_task_id:
            parent = self.session.exec(
                select(Task).where(Task.id == task.parent_task_id, Task.user_id == user_id)
            ).first()

        return {
            "task": task,
            "parent": parent,
            "children": children
        }

    def get_full_hierarchy(self, root_task_id: UUID, user_id: UUID) -> dict:
        """
        Gets the full hierarchy starting from a root task.

        Args:
            root_task_id: The ID of the root task
            user_id: The ID of the user

        Returns:
            Dictionary representing the full hierarchy tree
        """
        root_task = self.session.exec(
            select(Task).where(Task.id == root_task_id, Task.user_id == user_id)
        ).first()

        if not root_task:
            return None

        return {
            "task": root_task,
            "children": self._get_children_recursive(root_task_id, user_id)
        }

    def _get_children_recursive(self, parent_id: UUID, user_id: UUID) -> List[dict]:
        """
        Helper method to recursively get all children of a task.

        Args:
            parent_id: The ID of the parent task
            user_id: The ID of the user

        Returns:
            List of dictionaries representing child tasks and their subtrees
        """
        children = self.session.exec(
            select(Task).where(Task.parent_task_id == parent_id, Task.user_id == user_id)
        ).all()

        result = []
        for child in children:
            result.append({
                "task": child,
                "children": self._get_children_recursive(child.id, user_id)
            })

        return result

    def move_task_under_parent(self, task_id: UUID, new_parent_id: Optional[UUID], user_id: UUID) -> bool:
        """
        Moves a task under a new parent (or makes it a root task if new_parent_id is None).

        Args:
            task_id: The ID of the task to move
            new_parent_id: The ID of the new parent task (None to make it a root task)
            user_id: The ID of the user

        Returns:
            True if the move was successful, False otherwise
        """
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return False

        # Verify the new parent belongs to the same user (if not None)
        if new_parent_id:
            new_parent = self.session.exec(
                select(Task).where(Task.id == new_parent_id, Task.user_id == user_id)
            ).first()
            if not new_parent:
                return False

        # Update the parent_task_id
        task.parent_task_id = new_parent_id
        self.session.add(task)
        self.session.commit()

        return True

    def get_root_tasks(self, user_id: UUID) -> List[Task]:
        """
        Gets all root tasks (tasks with no parent) for a user.

        Args:
            user_id: The ID of the user

        Returns:
            List of root tasks
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.parent_task_id.is_(None)
        )
        return self.session.exec(statement).all()

    def count_descendants(self, task_id: UUID, user_id: UUID) -> int:
        """
        Counts all descendant tasks of a given task.

        Args:
            task_id: The ID of the task
            user_id: The ID of the user

        Returns:
            Number of descendant tasks
        """
        descendants = self._get_all_descendants(task_id, user_id)
        return len(descendants)

    def _get_all_descendants(self, parent_id: UUID, user_id: UUID) -> List[Task]:
        """
        Helper method to get all descendants of a task recursively.

        Args:
            parent_id: The ID of the parent task
            user_id: The ID of the user

        Returns:
            List of all descendant tasks
        """
        direct_children = self.session.exec(
            select(Task).where(Task.parent_task_id == parent_id, Task.user_id == user_id)
        ).all()

        all_descendants = list(direct_children)
        for child in direct_children:
            all_descendants.extend(self._get_all_descendants(child.id, user_id))

        return all_descendants