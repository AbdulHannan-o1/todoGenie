from typing import List
from sqlmodel import Session, select
from backend.src.models.task import Task

# Assuming a placeholder for a "deleted user" ID. In a real system, this would be a specific user ID
# or a more sophisticated mechanism for archiving/reassigning.
DELETED_USER_ID = 0 # Placeholder for a system-level "deleted user"

def reassign_user_tasks_on_delete(session: Session, user_id: int) -> List[Task]:
    """
    Reassigns all tasks from a deleted user to a designated 'deleted user' ID.
    In a more complex system, this might involve moving tasks to an archive,
    or marking them with a specific flag.
    """
    tasks_to_reassign = session.exec(select(Task).where(Task.user_id == user_id)).all()
    for task in tasks_to_reassign:
        task.user_id = DELETED_USER_ID # Reassign to the placeholder deleted user ID
        session.add(task)
    session.commit()
    return tasks_to_reassign