from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from uuid import UUID
import json

from ..models import Task
from ..db.session import get_session


class RecurringTaskService:
    """
    Service for handling recurring tasks functionality.
    Creates new task instances based on recurrence patterns.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_recurring_task_instance(self, original_task: Task) -> Optional[Task]:
        """
        Creates a new task instance based on the recurrence pattern of the original task.

        Args:
            original_task: The original recurring task

        Returns:
            New task instance if successfully created, None otherwise
        """
        if not original_task.recurrence_pattern:
            return None

        recurrence_pattern = original_task.recurrence_pattern

        # Calculate next occurrence date based on the pattern
        next_due_date = self._calculate_next_occurrence(
            original_task.due_date,
            recurrence_pattern
        )

        if not next_due_date:
            return None

        # Create new task with updated dates
        new_task = Task(
            title=original_task.title,
            description=original_task.description,
            status="pending",
            priority=original_task.priority,
            recurrence_pattern=original_task.recurrence_pattern,
            due_date=next_due_date,
            reminder_time=self._calculate_next_reminder_time(
                original_task.reminder_time,
                original_task.due_date,
                next_due_date
            ),
            tags=original_task.tags,
            parent_task_id=original_task.parent_task_id,
            user_id=original_task.user_id,
            ai_generated=original_task.ai_generated,
            ai_intent=original_task.ai_intent,
            ai_context_id=original_task.ai_context_id
        )

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)

        return new_task

    def _calculate_next_occurrence(self, last_due_date: Optional[datetime], pattern: Dict[str, Any]) -> Optional[datetime]:
        """
        Calculates the next occurrence date based on the recurrence pattern.

        Args:
            last_due_date: The last occurrence date
            pattern: The recurrence pattern dictionary

        Returns:
            Next occurrence date or None if no further occurrences
        """
        if not last_due_date:
            # If no last due date, use current time
            last_due_date = datetime.now()

        frequency = pattern.get('frequency', 'daily')
        interval = pattern.get('interval', 1)
        end_condition = pattern.get('end_condition', {})

        # Check if the recurrence should end
        if self._should_end_recurrence(end_condition, last_due_date):
            return None

        # Calculate next occurrence based on frequency
        if frequency == 'daily':
            next_date = last_due_date + timedelta(days=interval)
        elif frequency == 'weekly':
            next_date = last_due_date + timedelta(weeks=interval)
        elif frequency == 'monthly':
            # For monthly recurrence, we'll add months
            # This is a simplified version - in practice you'd want to handle month-end edge cases
            import calendar
            year = last_due_date.year
            month = last_due_date.month + interval

            # Adjust for year overflow
            while month > 12:
                year += 1
                month -= 12

            # Get the number of days in the target month
            max_day = calendar.monthrange(year, month)[1]
            day = min(last_due_date.day, max_day)

            next_date = last_due_date.replace(year=year, month=month, day=day)
        elif frequency == 'yearly':
            next_date = last_due_date.replace(year=last_due_date.year + interval)
        elif frequency == 'custom':
            # For custom patterns, we could support more complex rules
            # For now, treat as daily with custom interval
            next_date = last_due_date + timedelta(days=interval)
        else:
            # Unknown frequency, default to daily
            next_date = last_due_date + timedelta(days=1)

        return next_date

    def _should_end_recurrence(self, end_condition: Dict[str, Any], current_date: datetime) -> bool:
        """
        Checks if the recurrence should end based on the end condition.

        Args:
            end_condition: Dictionary containing end condition rules
            current_date: Current date to compare against

        Returns:
            True if recurrence should end, False otherwise
        """
        end_type = end_condition.get('type', 'never')

        if end_type == 'never':
            return False
        elif end_type == 'on_date':
            end_date_str = end_condition.get('value')
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                return current_date >= end_date
        elif end_type == 'after_occurrences':
            # This would require tracking how many occurrences have happened
            # For now, we'll return False - in a full implementation this would check a counter
            return False

        return False

    def _calculate_next_reminder_time(self, last_reminder: Optional[datetime],
                                    last_due_date: Optional[datetime],
                                    next_due_date: datetime) -> Optional[datetime]:
        """
        Calculates the next reminder time based on the original relationship between
        the reminder and due date.

        Args:
            last_reminder: The last reminder time
            last_due_date: The last due date
            next_due_date: The next due date

        Returns:
            Next reminder time or None if no reminder was set
        """
        if not last_reminder or not last_due_date:
            return None

        # Calculate the time difference between due date and reminder
        time_diff = last_due_date - last_reminder

        # Apply the same difference to the next due date
        next_reminder = next_due_date - time_diff

        # Ensure the reminder is not after the due date
        if next_reminder >= next_due_date:
            return next_due_date  # Just set reminder to due date if calculation goes wrong

        return next_reminder

    def process_completed_recurring_task(self, task_id: UUID) -> Optional[Task]:
        """
        Processes a completed recurring task and creates the next instance if needed.

        Args:
            task_id: ID of the completed task

        Returns:
            New task instance if created, None otherwise
        """
        # Get the completed task
        completed_task = self.session.get(Task, task_id)

        if not completed_task or not completed_task.recurrence_pattern:
            return None

        # Create the next instance of the recurring task
        return self.create_recurring_task_instance(completed_task)