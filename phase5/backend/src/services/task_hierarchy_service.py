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

    def get_task_children(self, task_id: UUID, user_id: UUID) -> List[Task]:
        """
        Get all child tasks for a parent task.

        Args:
            task_id: The ID of the parent task
            user_id: The ID of the user

        Returns:
            List of child tasks
        """
        # Verify the parent task exists and belongs to the user
        parent_task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not parent_task:
            return []

        # Get all tasks that have this task as their parent
        children = self.session.exec(
            select(Task).where(Task.parent_task_id == task_id, Task.user_id == user_id)
        ).all()

        return children

    def create_child_task(self, parent_task_id: UUID, task_create_request, user_id: UUID) -> Task:
        """
        Create a child task under a parent task.

        Args:
            parent_task_id: The ID of the parent task
            task_create_request: The task creation request object
            user_id: The ID of the user

        Returns:
            The created child task
        """
        # Verify the parent task exists and belongs to the user
        parent_task = self.session.exec(
            select(Task).where(Task.id == parent_task_id, Task.user_id == user_id)
        ).first()

        if not parent_task:
            raise ValueError("Parent task not found or not owned by user")

        # Create the child task with the parent_task_id set
        task_data = task_create_request.model_dump()
        child_task = Task(
            user_id=user_id,
            parent_task_id=parent_task_id,
            title=task_data.get('title'),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            recurrence_pattern=task_data.get('recurrence_pattern'),
            due_date=task_data.get('due_date'),
            reminder_time=task_data.get('reminder_time'),
            tags=task_data.get('tags', ''),
            ai_generated=task_data.get('ai_generated', False),
            ai_intent=task_data.get('ai_intent'),
            ai_context_id=task_data.get('ai_context_id')
        )

        self.session.add(child_task)
        self.session.commit()
        self.session.refresh(child_task)

        return child_task

    def get_task_ancestors(self, task_id: UUID, user_id: UUID) -> List[Task]:
        """
        Get all ancestor tasks for a child task (returns the parent and higher-level ancestors).

        Args:
            task_id: The ID of the child task
            user_id: The ID of the user

        Returns:
            List of ancestor tasks in order from direct parent to top-level ancestor
        """
        # Verify the task exists and belongs to the user
        current_task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not current_task:
            return []

        ancestors = []
        current_parent_id = current_task.parent_task_id

        # Traverse up the hierarchy to find all ancestors
        while current_parent_id:
            parent_task = self.session.exec(
                select(Task).where(Task.id == current_parent_id, Task.user_id == user_id)
            ).first()

            if parent_task:
                ancestors.append(parent_task)
                current_parent_id = parent_task.parent_task_id
            else:
                break  # Parent not found, stop traversal

        # Return ancestors in order from direct parent to top-level ancestor
        return list(reversed(ancestors))