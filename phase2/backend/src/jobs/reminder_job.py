from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.src.models.task import Task
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

def send_reminders(session: Session):
    logger.info("Checking for task reminders to send...")
    now = datetime.now()
    reminder_window = now + timedelta(minutes=30)

    statement = select(Task).where(
        Task.due_date >= now,
        Task.due_date <= reminder_window,
        Task.status != "completed"
    )
    tasks_to_remind = session.exec(statement).all()

    for task in tasks_to_remind:
        logger.info(f"Sending reminder for task: {task.title} (due at {task.due_date})")
        # In a real application, this would trigger an email, push notification, etc.
