"""
Task operations service for handling todo operations called by the AI agent
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session, select
from src.db import get_session
from src.models import Task, User
from src.models.conversation import Message


class TaskOperationsService:
    @staticmethod
    def create_task(title: str, description: Optional[str], user_id: str,
                   tags: Optional[str] = None, priority: Optional[str] = None,
                   due_date: Optional[str] = None, reminder_time: Optional[str] = None,
                   recurrence_pattern: Optional[Dict] = None, parent_task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task for the user with advanced features
        """
        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id)

                # Validate priority if provided
                valid_priorities = ["low", "medium", "high", "urgent"]
                if priority and priority.lower() not in valid_priorities:
                    priority = None  # Ignore invalid priority

                # Parse due_date if provided
                due_date_obj = None
                if due_date:
                    from datetime import datetime
                    try:
                        due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        # If date parsing fails, ignore it
                        pass

                # Parse reminder_time if provided
                reminder_time_obj = None
                if reminder_time:
                    from datetime import datetime
                    try:
                        reminder_time_obj = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        # If date parsing fails, ignore it
                        pass

                # Validate parent_task_id if provided
                parent_task_uuid = None
                if parent_task_id:
                    try:
                        parent_task_uuid = UUID(parent_task_id)
                        # Verify parent task exists and belongs to the same user
                        parent_task = session.get(Task, parent_task_uuid)
                        if not parent_task or parent_task.user_id != user_uuid:
                            parent_task_uuid = None  # Invalid parent, ignore
                    except ValueError:
                        # Invalid UUID format
                        parent_task_uuid = None

                # Create new task
                task = Task(
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    tags=tags or "",
                    priority=priority.lower() if priority else "medium",  # Default to medium
                    due_date=due_date_obj,
                    reminder_time=reminder_time_obj,
                    recurrence_pattern=recurrence_pattern,
                    parent_task_id=parent_task_uuid,
                    ai_generated=True,  # Mark as AI-generated
                    ai_intent="create_task"
                )

                session.add(task)
                session.commit()
                session.refresh(task)

                return {
                    "status": "success",
                    "message": f"Task '{task.title}' created successfully",
                    "task_id": str(task.id),
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "recurrence_pattern": task.recurrence_pattern,
                        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create task: {str(e)}"
            }

    @staticmethod
    def list_tasks(user_id: str, include_completed: bool = True,
                   priority_filter: Optional[str] = None,
                   due_date_start: Optional[str] = None,
                   due_date_end: Optional[str] = None) -> Dict[str, Any]:
        """
        List all tasks for the user with optional filters
        """
        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id)

                # Start building the query
                statement = select(Task).where(Task.user_id == user_uuid)

                # Apply filters
                if not include_completed:
                    statement = statement.where(Task.status != "completed")

                if priority_filter:
                    statement = statement.where(Task.priority == priority_filter.lower())

                if due_date_start:
                    from datetime import datetime
                    try:
                        start_date = datetime.fromisoformat(due_date_start.replace('Z', '+00:00'))
                        statement = statement.where(Task.due_date >= start_date)
                    except (ValueError, AttributeError):
                        pass  # Ignore invalid date

                if due_date_end:
                    from datetime import datetime
                    try:
                        end_date = datetime.fromisoformat(due_date_end.replace('Z', '+00:00'))
                        statement = statement.where(Task.due_date <= end_date)
                    except (ValueError, AttributeError):
                        pass  # Ignore invalid date

                # Execute the query
                tasks = session.exec(statement).all()

                task_list = []
                for task in tasks:
                    task_dict = {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "tags": task.tags,
                        "recurrence_pattern": task.recurrence_pattern,
                        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                    }
                    task_list.append(task_dict)

                return {
                    "status": "success",
                    "message": f"Found {len(task_list)} tasks",
                    "tasks": task_list
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list tasks: {str(e)}"
            }

    @staticmethod
    def update_task(task_id: str, title: Optional[str] = None, description: Optional[str] = None,
                    status: Optional[str] = None, priority: Optional[str] = None,
                    due_date: Optional[str] = None, reminder_time: Optional[str] = None,
                    tags: Optional[str] = None, recurrence_pattern: Optional[Dict] = None,
                    parent_task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task with advanced features
        """
        try:
            # Validate task ID format
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Invalid task ID format: {task_id}"
                }

            with next(get_session()) as session:
                # Get the task
                task = session.get(Task, task_uuid)
                if not task:
                    return {
                        "status": "error",
                        "message": f"Task with ID {task_id} not found"
                    }

                # Validate status if provided
                valid_statuses = ["pending", "in progress", "completed", "archived", "cancelled"]
                if status is not None and status.lower() not in valid_statuses:
                    return {
                        "status": "error",
                        "message": f"Invalid status: {status}. Valid statuses are: {', '.join(valid_statuses)}"
                    }

                # Validate priority if provided
                valid_priorities = ["low", "medium", "high", "urgent"]
                if priority is not None and priority.lower() not in valid_priorities:
                    return {
                        "status": "error",
                        "message": f"Invalid priority: {priority}. Valid priorities are: {', '.join(valid_priorities)}"
                    }

                # Validate parent_task_id if provided
                parent_task_uuid = task.parent_task_id  # Keep existing value as default
                if parent_task_id is not None and parent_task_id != "":
                    if parent_task_id.lower() == "null" or parent_task_id.lower() == "none":
                        parent_task_uuid = None  # Remove parent relationship
                    else:
                        try:
                            parent_task_uuid = UUID(parent_task_id)
                            # Verify parent task exists and belongs to the same user
                            parent_task = session.get(Task, parent_task_uuid)
                            if not parent_task or parent_task.user_id != task.user_id:
                                return {
                                    "status": "error",
                                    "message": f"Parent task with ID {parent_task_id} not found or doesn't belong to user"
                                }
                        except ValueError:
                            return {
                                "status": "error",
                                "message": f"Invalid parent task ID format: {parent_task_id}"
                            }

                # Update fields if provided
                if title is not None:
                    task.title = title
                if description is not None:
                    task.description = description
                if status is not None:
                    task.status = status.lower()
                if priority is not None:
                    task.priority = priority.lower()
                if due_date is not None:
                    from datetime import datetime
                    try:
                        task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        return {
                            "status": "error",
                            "message": f"Invalid due date format: {due_date}. Use ISO format (e.g., 2023-12-25T10:30:00)"
                        }
                if reminder_time is not None:
                    from datetime import datetime
                    try:
                        task.reminder_time = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
                    except ValueError:
                        return {
                            "status": "error",
                            "message": f"Invalid reminder time format: {reminder_time}. Use ISO format (e.g., 2023-12-25T10:30:00)"
                        }
                if tags is not None:
                    task.tags = tags
                if recurrence_pattern is not None:
                    task.recurrence_pattern = recurrence_pattern
                if parent_task_id is not None:  # This could be an empty string to remove parent
                    task.parent_task_id = parent_task_uuid

                # Mark as AI-updated
                task.ai_generated = True
                task.ai_intent = "update_task"

                session.add(task)
                session.commit()
                session.refresh(task)

                return {
                    "status": "success",
                    "message": f"Task '{task.title}' updated successfully",
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "tags": task.tags,
                        "recurrence_pattern": task.recurrence_pattern,
                        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update task: {str(e)}"
            }

    @staticmethod
    def delete_task(task_id: str) -> Dict[str, Any]:
        """
        Delete a task
        """
        try:
            with next(get_session()) as session:
                task_uuid = UUID(task_id)

                # Get the task
                task = session.get(Task, task_uuid)
                if not task:
                    return {
                        "status": "error",
                        "message": f"Task with ID {task_id} not found"
                    }

                session.delete(task)
                session.commit()

                return {
                    "status": "success",
                    "message": f"Task '{task.title}' deleted successfully"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete task: {str(e)}"
            }

    @staticmethod
    def complete_task(task_id: str, completed: bool = True) -> Dict[str, Any]:
        """
        Mark a task as complete/incomplete
        """
        try:
            status = "completed" if completed else "pending"
            return TaskOperationsService.update_task(task_id, status=status)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update task completion status: {str(e)}"
            }


    @staticmethod
    def get_child_tasks(task_id: str) -> List[Dict[str, Any]]:
        """
        Get all child tasks for a parent task
        """
        try:
            with next(get_session()) as session:
                parent_uuid = UUID(task_id)

                # Verify parent task exists
                parent_task = session.get(Task, parent_uuid)
                if not parent_task:
                    return {
                        "status": "error",
                        "message": f"Parent task with ID {task_id} not found"
                    }

                # Find all tasks that have this task as parent
                statement = select(Task).where(Task.parent_task_id == parent_uuid)
                child_tasks = session.exec(statement).all()

                child_tasks_list = []
                for task in child_tasks:
                    task_dict = {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "tags": task.tags,
                        "recurrence_pattern": task.recurrence_pattern,
                        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                    }
                    child_tasks_list.append(task_dict)

                return {
                    "status": "success",
                    "message": f"Found {len(child_tasks_list)} child tasks",
                    "tasks": child_tasks_list
                }
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid task ID format: {task_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get child tasks: {str(e)}"
            }

    @staticmethod
    def create_child_task(parent_task_id: str, title: str, description: Optional[str] = None,
                         user_id: str = "", tags: Optional[str] = None,
                         priority: Optional[str] = None, due_date: Optional[str] = None,
                         reminder_time: Optional[str] = None,
                         recurrence_pattern: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a child task under a parent task
        """
        try:
            parent_uuid = UUID(parent_task_id)

            # Validate user_id if provided
            user_uuid = None
            if user_id:
                user_uuid = UUID(user_id)

            with next(get_session()) as session:
                # Verify parent task exists
                parent_task = session.get(Task, parent_uuid)
                if not parent_task:
                    return {
                        "status": "error",
                        "message": f"Parent task with ID {parent_task_id} not found"
                    }

                # Use parent task's user if user_id not provided
                if not user_uuid:
                    user_uuid = parent_task.user_id

                # Validate priority if provided
                valid_priorities = ["low", "medium", "high", "urgent"]
                if priority and priority.lower() not in valid_priorities:
                    priority = None  # Ignore invalid priority

                # Parse due_date if provided
                due_date_obj = None
                if due_date:
                    from datetime import datetime
                    try:
                        due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        # If date parsing fails, ignore it
                        pass

                # Parse reminder_time if provided
                reminder_time_obj = None
                if reminder_time:
                    from datetime import datetime
                    try:
                        reminder_time_obj = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        # If date parsing fails, ignore it
                        pass

                # Create child task
                child_task = Task(
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    tags=tags or "",
                    priority=priority.lower() if priority else "medium",  # Default to medium
                    due_date=due_date_obj,
                    reminder_time=reminder_time_obj,
                    recurrence_pattern=recurrence_pattern,
                    parent_task_id=parent_uuid,  # Set the parent relationship
                    ai_generated=True,  # Mark as AI-generated
                    ai_intent="create_child_task"
                )

                session.add(child_task)
                session.commit()
                session.refresh(child_task)

                return {
                    "status": "success",
                    "message": f"Child task '{child_task.title}' created successfully under parent task",
                    "task_id": str(child_task.id),
                    "task": {
                        "id": str(child_task.id),
                        "title": child_task.title,
                        "description": child_task.description,
                        "status": child_task.status,
                        "priority": child_task.priority,
                        "due_date": child_task.due_date.isoformat() if child_task.due_date else None,
                        "reminder_time": child_task.reminder_time.isoformat() if child_task.reminder_time else None,
                        "tags": child_task.tags,
                        "recurrence_pattern": child_task.recurrence_pattern,
                        "parent_task_id": str(child_task.parent_task_id) if child_task.parent_task_id else None
                    }
                }
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid task ID format: {parent_task_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create child task: {str(e)}"
            }

    @staticmethod
    def get_upcoming_reminders(user_id: str, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming reminders for a user within the specified hours
        """
        try:
            user_uuid = UUID(user_id)
            from datetime import datetime, timedelta, timezone

            with next(get_session()) as session:
                # Calculate the future time threshold (UTC aware to match model)
                threshold_time = datetime.now(timezone.utc) + timedelta(hours=hours_ahead)

                # Find tasks with reminder times within the specified window
                statement = select(Task).where(
                    (Task.user_id == user_uuid) &
                    (Task.reminder_time.is_not(None)) &  # Has a reminder time
                    (Task.reminder_time <= threshold_time) &  # Reminder is within the time window
                    (Task.status != "completed")  # Task is not completed
                ).order_by(Task.reminder_time)

                upcoming_tasks = session.exec(statement).all()

                reminder_list = []
                for task in upcoming_tasks:
                    task_dict = {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "tags": task.tags,
                        "recurrence_pattern": task.recurrence_pattern,
                        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                    }
                    reminder_list.append(task_dict)

                return {
                    "status": "success",
                    "message": f"Found {len(reminder_list)} upcoming reminders",
                    "reminders": reminder_list
                }
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid user ID format: {user_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get upcoming reminders: {str(e)}"
            }

    @staticmethod
    def get_task_by_id(task_id: str) -> Dict[str, Any]:
        """
        Get a specific task by ID
        """
        try:
            task_uuid = UUID(task_id)

            with next(get_session()) as session:
                task = session.get(Task, task_uuid)
                if not task:
                    return {
                        "status": "error",
                        "message": f"Task with ID {task_id} not found"
                    }

                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "tags": task.tags,
                    "recurrence_pattern": task.recurrence_pattern,
                    "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
                }

                return {
                    "status": "success",
                    "message": "Task retrieved successfully",
                    "task": task_dict
                }
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid task ID format: {task_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get task: {str(e)}"
            }


# Global task operations service instance
task_operations_service = TaskOperationsService()