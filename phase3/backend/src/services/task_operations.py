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
    def list_tasks(
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List tasks for user with optional filters
        
        Parameters:
        - user_id: User's UUID
        - status: "pending", "completed", or "all"
        - priority: "high", "medium", or "low"
        - tags: Comma-separated tags
        - search: Keyword search in title/description
        
        Returns:
        - Dict with status, message, tasks list, and applied filters
        """
        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id)
                
                # Build query
                statement = select(Task).where(Task.user_id == user_uuid)
                
                # Apply filters
                if status and status != "all":
                    is_completed = status.lower() == "completed"
                    statement = statement.where(Task.completed == is_completed)
                
                if priority:
                    statement = statement.where(Task.priority == priority.lower())
                
                if tags:
                    tag_list = [t.strip() for t in tags.split(",")]
                    # Search in tags field (comma-separated string)
                    for tag in tag_list:
                        statement = statement.where(Task.tags.contains(tag))
                
                if search:
                    # Search in title and description
                    statement = statement.where(
                        (Task.title.contains(search)) | 
                        (Task.description.contains(search))
                    )
                
                tasks = session.exec(statement).all()
                
                task_list = []
                for task in tasks:
                    task_list.append({
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending",
                        "priority": task.priority,
                        "tags": task.tags,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    })
                
                return {
                    "status": "success",
                    "message": f"Found {len(task_list)} tasks",
                    "tasks": task_list,
                    "filters_applied": {
                        "status": status,
                        "priority": priority,
                        "tags": tags,
                        "search": search
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list tasks: {str(e)}"
            }

    @staticmethod
    def get_task_details(task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific task
        
        Parameters:
        - task_id: UUID of the task
        - user_id: User's UUID for ownership verification
        
        Returns:
        - Dict with status, task details, or error message
        """
        try:
            with next(get_session()) as session:
                task_uuid = UUID(task_id)
                task = session.get(Task, task_uuid)
                
                if not task:
                    return {
                        "status": "error",
                        "message": f"Task {task_id} not found"
                    }
                
                # Verify ownership
                if str(task.user_id) != user_id:
                    return {
                        "status": "error",
                        "message": "Access denied: Task does not belong to user"
                    }
                
                return {
                    "status": "success",
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending",
                        "priority": task.priority,
                        "tags": task.tags,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get task details: {str(e)}"
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