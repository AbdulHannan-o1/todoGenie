from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from ..models import Task, Notification
from ..db.session import get_session


class ReminderService:
    """
    Service for handling due date reminders and notifications.
    Schedules and sends notifications for upcoming task due dates.
    """

    def __init__(self, session: Session):
        self.session = session
        self.executor = ThreadPoolExecutor(max_workers=5)

    def schedule_reminders_for_task(self, task: Task) -> bool:
        """
        Schedules a reminder for a task if it has a due date and reminder time.

        Args:
            task: The task to schedule reminders for

        Returns:
            True if reminder was scheduled, False otherwise
        """
        if not task.reminder_time or not task.due_date:
            return False

        # Create a notification record for the reminder
        notification = Notification(
            user_id=task.user_id,
            task_id=task.id,
            type="reminder",
            message=f"Reminder: '{task.title}' is due soon!",
            scheduled_time=task.reminder_time,
            status="scheduled"
        )

        self.session.add(notification)
        self.session.commit()

        return True

    def schedule_reminders_for_user_tasks(self, user_id: UUID) -> int:
        """
        Schedules reminders for all tasks of a user that have due dates and reminder times.

        Args:
            user_id: The ID of the user

        Returns:
            Number of reminders scheduled
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.reminder_time.is_not(None),
            Task.due_date.is_not(None)
        )
        tasks = self.session.exec(statement).all()

        scheduled_count = 0
        for task in tasks:
            if self.schedule_reminders_for_task(task):
                scheduled_count += 1

        return scheduled_count

    def check_and_send_due_date_reminders(self) -> int:
        """
        Checks for due date reminders that should be sent now and sends them.

        Returns:
            Number of reminders sent
        """
        now = datetime.now()

        # Find all scheduled notifications that should be sent now
        statement = select(Notification).where(
            Notification.status == "scheduled",
            Notification.scheduled_time <= now
        )
        notifications = self.session.exec(statement).all()

        sent_count = 0
        for notification in notifications:
            # In a real implementation, this would send the actual notification
            # (via WebSocket, email, browser notification, etc.)
            # For now, we'll just update the status

            notification.status = "sent"
            notification.sent_time = now
            self.session.add(notification)

            sent_count += 1

        self.session.commit()
        return sent_count

    def get_upcoming_reminders(self, user_id: UUID, hours_ahead: int = 24) -> List[Notification]:
        """
        Gets upcoming reminders for a user within a specified time window.

        Args:
            user_id: The ID of the user
            hours_ahead: Number of hours ahead to look for reminders

        Returns:
            List of upcoming notifications
        """
        now = datetime.now()
        future_time = now + timedelta(hours=hours_ahead)

        statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.status == "scheduled",
            Notification.scheduled_time >= now,
            Notification.scheduled_time <= future_time
        ).order_by(Notification.scheduled_time)

        return self.session.exec(statement).all()

    def cancel_reminder(self, notification_id: UUID) -> bool:
        """
        Cancels a scheduled reminder.

        Args:
            notification_id: The ID of the notification to cancel

        Returns:
            True if cancellation was successful, False otherwise
        """
        notification = self.session.get(Notification, notification_id)

        if not notification or notification.status != "scheduled":
            return False

        notification.status = "cancelled"
        self.session.add(notification)
        self.session.commit()

        return True

    def cleanup_expired_reminders(self) -> int:
        """
        Cleans up expired reminders that were not sent.

        Returns:
            Number of expired reminders cleaned up
        """
        now = datetime.now()

        # Find notifications that were scheduled for the past but never sent
        statement = select(Notification).where(
            Notification.status == "scheduled",
            Notification.scheduled_time < now - timedelta(hours=1)  # Cleanup reminders older than 1 hour that weren't sent
        )
        expired_notifications = self.session.exec(statement).all()

        cleaned_count = 0
        for notification in expired_notifications:
            notification.status = "failed"  # Mark as failed to indicate it wasn't sent in time
            self.session.add(notification)
            cleaned_count += 1

        self.session.commit()
        return cleaned_count
