from datetime import datetime, timedelta
from sqlmodel import Session, select
from ..models import Task
from ..utils.logger import get_logger
from typing import Callable, Generator

logger = get_logger(__name__)

def send_reminders(get_session_callable: Callable[[], Generator[Session, None, None]]):
    logger.info("Checking for task reminders and overdue tasks...")
    now = datetime.now()
    reminder_window = now + timedelta(minutes=30)

    session = None
    try:
        session = next(get_session_callable())

        # Find tasks that are due soon (for reminders)
        upcoming_tasks_statement = select(Task).where(
            Task.due_date >= now,
            Task.due_date <= reminder_window,
            Task.status != "completed"
        )
        upcoming_tasks = session.exec(upcoming_tasks_statement).all()

        # Find tasks that are overdue (past due date and not completed)
        overdue_tasks_statement = select(Task).where(
            Task.due_date < now,
            Task.status != "completed"
        )
        overdue_tasks = session.exec(overdue_tasks_statement).all()

        # Send reminders for upcoming tasks
        for task in upcoming_tasks:
            logger.info(f"Sending reminder for task: {task.title} (due at {task.due_date})")
            # In a real application, this would trigger an email, push notification, etc.

        # Log overdue tasks (in a real app, you might want to send notifications for these too)
        for task in overdue_tasks:
            logger.info(f"Task is overdue: {task.title} (was due at {task.due_date})")
            # In a real application, this would trigger overdue notifications, etc.
    finally:
        if session:
            session.close()
