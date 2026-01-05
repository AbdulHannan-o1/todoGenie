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
                   due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task for the user
        """
        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id)

                # Validate priority if provided
                if priority and priority.lower() not in ["low", "medium", "high"]:
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

                # Create new task
                task = Task(
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    tags=tags or "",
                    priority=priority.lower() if priority else None,
                    due_date=due_date_obj,
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
                        "status": task.status
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create task: {str(e)}"
            }

    @staticmethod
    def list_tasks(user_id: str) -> Dict[str, Any]:
        """
        List all tasks for the user
        """
        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id)

                # Query tasks for the user
                statement = select(Task).where(Task.user_id == user_uuid)
                tasks = session.exec(statement).all()

                task_list = []
                for task in tasks:
                    task_list.append({
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    })

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
                    due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task
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
                valid_priorities = ["low", "medium", "high"]
                if priority is not None and priority.lower() not in valid_priorities:
                    return {
                        "status": "error",
                        "message": f"Invalid priority: {priority}. Valid priorities are: {', '.join(valid_priorities)}"
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
                            "message": f"Invalid date format: {due_date}. Use ISO format (e.g., 2023-12-25T10:30:00)"
                        }

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
                        "status": task.status
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


# Global task operations service instance
task_operations_service = TaskOperationsService()