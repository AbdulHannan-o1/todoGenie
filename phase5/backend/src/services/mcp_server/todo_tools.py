"""
MCP tools for todo operations that can be called by the AI agent
"""
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
import aiomcp
from src.services.task_operations import TaskOperationsService
import re
from difflib import get_close_matches


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID


class RecurrencePattern(BaseModel):
    frequency: str  # daily, weekly, monthly, yearly, custom
    interval: int = 1
    end_condition: Optional[Dict] = None  # {type: 'never', 'on_date', 'after_occurrences', value: date or count}


class TaskUpdateRequest(BaseModel):
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    reminder_time: Optional[str] = None
    tags: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    parent_task_id: Optional[str] = None


class TaskCompleteRequest(BaseModel):
    task_id: UUID
    completed: bool = True


def create_task_tool(title: str, description: Optional[str] = None, user_id: str = "",
                    tags: Optional[str] = None, priority: Optional[str] = None,
                    due_date: Optional[str] = None, reminder_time: Optional[str] = None,
                    recurrence_pattern: Optional[Dict] = None, parent_task_id: Optional[str] = None) -> Dict:
    """
    Create a new task via tool with optional tags, priority, due_date, reminders, recurrence, and hierarchical relationships
    """
    return TaskOperationsService.create_task(
        title, description, user_id, tags, priority, due_date,
        reminder_time, recurrence_pattern, parent_task_id
    )


def list_tasks_tool(user_id: str = "", include_completed: bool = True,
                   priority_filter: Optional[str] = None,
                   due_date_start: Optional[str] = None,
                   due_date_end: Optional[str] = None) -> List[Dict]:
    """
    List all tasks for a user via tool with optional filters
    """
    result = TaskOperationsService.list_tasks(
        user_id, include_completed, priority_filter, due_date_start, due_date_end
    )
    return result.get("tasks", [])


def update_task_tool(task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    due_date: Optional[str] = None,
                    reminder_time: Optional[str] = None,
                    tags: Optional[str] = None,
                    recurrence_pattern: Optional[Dict] = None,
                    parent_task_id: Optional[str] = None) -> Dict:
    """
    Update an existing task via tool with advanced features
    """
    return TaskOperationsService.update_task(
        task_id, title, description, status, priority, due_date,
        reminder_time, tags, recurrence_pattern, parent_task_id
    )


def delete_task_tool(task_id: str) -> Dict:
    """
    Delete a task via tool
    """
    return TaskOperationsService.delete_task(task_id)


def complete_task_tool(task_id: str, completed: bool = True) -> Dict:
    """
    Mark a task as complete/incomplete via tool
    """
    return TaskOperationsService.complete_task(task_id, completed)


def get_child_tasks_tool(task_id: str) -> List[Dict]:
    """
    Get all child tasks for a parent task
    """
    return TaskOperationsService.get_child_tasks(task_id)


def create_child_task_tool(parent_task_id: str, title: str, description: Optional[str] = None,
                          user_id: str = "", tags: Optional[str] = None,
                          priority: Optional[str] = None, due_date: Optional[str] = None,
                          reminder_time: Optional[str] = None,
                          recurrence_pattern: Optional[Dict] = None) -> Dict:
    """
    Create a child task under a parent task
    """
    return TaskOperationsService.create_child_task(
        parent_task_id, title, description, user_id, tags, priority,
        due_date, reminder_time, recurrence_pattern
    )


def get_upcoming_reminders_tool(user_id: str, hours_ahead: int = 24) -> List[Dict]:
    """
    Get upcoming reminders for a user
    """
    return TaskOperationsService.get_upcoming_reminders(user_id, hours_ahead)


def get_task_by_id_tool(task_id: str) -> Dict:
    """
    Get a specific task by ID
    """
    return TaskOperationsService.get_task_by_id(task_id)


def _find_tasks_by_criteria(user_id: str, title: Optional[str] = None,
                           priority: Optional[str] = None,
                           status: Optional[str] = None,
                           include_completed: bool = False) -> List[Dict]:
    """
    Helper function to find tasks by various criteria (title, description, priority, status)
    Matches against both title AND description fields for flexibility
    """
    # Get all tasks for the user
    all_tasks_result = TaskOperationsService.list_tasks(
        user_id=user_id,
        include_completed=include_completed
    )

    if all_tasks_result.get("status") != "success":
        return []

    tasks = all_tasks_result.get("tasks", [])
    filtered_tasks = []

    # Apply filters
    for task in tasks:
        match = True

        # Check title or description match (case-insensitive partial match)
        # This allows matching by task name OR description
        if title:
            task_title = task.get("title") or ""
            task_description = task.get("description") or ""
            title_lower = title.lower() if title else ""
            title_match = title_lower in task_title.lower()
            description_match = title_lower in task_description.lower()
            if not (title_match or description_match):
                match = False

        # Check priority match
        if priority and task.get("priority", "").lower() != priority.lower():
            match = False

        # Check status match
        if status and task.get("status", "").lower() != status.lower():
            match = False

        if match:
            filtered_tasks.append(task)

    return filtered_tasks


def complete_task_by_description(title: str = None, priority: str = None,
                               user_id: str = "", status: str = "pending") -> Dict:
    """
    Complete tasks based on description criteria instead of ID
    """
    try:
        # Find tasks matching the criteria
        matching_tasks = _find_tasks_by_criteria(
            user_id=user_id,
            title=title,
            priority=priority,
            status=status,
            include_completed=False  # Only incomplete tasks
        )

        if not matching_tasks:
            # If no exact match, try fuzzy matching for title and description
            if title:
                all_tasks_result = TaskOperationsService.list_tasks(
                    user_id=user_id,
                    include_completed=False
                )

                if all_tasks_result.get("status") == "success":
                    all_tasks = all_tasks_result.get("tasks", [])

                    # Use fuzzy matching to find tasks with similar titles or descriptions
                    titles = [task.get("title", "") for task in all_tasks]
                    descriptions = [task.get("description", "") for task in all_tasks]

                    # Search in titles - handle None title safely
                    title_lower = title.lower() if title else ""
                    if title_lower:
                        close_matches = get_close_matches(title_lower,
                                                       [t.lower() for t in titles if t],
                                                       n=3, cutoff=0.3)

                        # Also search in descriptions if title search didn't find anything
                        if not close_matches:
                            close_matches = get_close_matches(title_lower,
                                                           [d.lower() for d in descriptions if d],
                                                           n=3, cutoff=0.3)

                        if close_matches:
                            # Find the tasks that correspond to the close matches (search both title and description)
                            for task in all_tasks:
                                task_title = task.get("title", "").lower()
                                task_desc = task.get("description", "").lower()
                                task_matched = (
                                    task_title in [match.lower() for match in close_matches] or
                                    task_desc in [match.lower() for match in close_matches]
                                )
                                if task_matched:
                                    matching_tasks.append(task)

        if not matching_tasks:
            return {
                "status": "error",
                "message": f"No tasks found matching the criteria: title='{title}', priority='{priority}', status='{status}'"
            }

        # CRITICAL: Prevent completing multiple tasks without explicit confirmation
        if len(matching_tasks) > 1:
            task_list = "\n".join([f"  • {t.get('title', 'Unknown')} (ID: {t.get('id', 'N/A')})" 
                                   for t in matching_tasks])
            return {
                "status": "ambiguous",
                "message": f"Found {len(matching_tasks)} matching tasks. Please clarify which one(s) to complete:\n{task_list}",
                "tasks": matching_tasks
            }

        # Complete the single matching task
        completed_count = 0
        failed_tasks = []

        for task in matching_tasks:
            result = TaskOperationsService.complete_task(task["id"], completed=True)
            if result.get("status") == "success":
                completed_count += 1
            else:
                failed_tasks.append(task.get("title", "Unknown Task"))

        if completed_count > 0:
            return {
                "status": "success",
                "message": f"Successfully completed {completed_count} task(s)",
                "completed_tasks_count": completed_count,
                "failed_tasks": failed_tasks
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to complete any tasks. Errors occurred with: {', '.join(failed_tasks) if failed_tasks else 'Unknown error'}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to complete tasks by description: {str(e)}"
        }


def update_tasks_by_description(title: str = None, priority: str = None,
                              user_id: str = "", status: str = None,
                              new_title: str = None, description: str = None,
                              due_date: str = None, reminder_time: str = None,
                              tags: str = None, recurrence_pattern: Dict = None,
                              parent_task_id: str = None) -> Dict:
    """
    Update multiple tasks based on description criteria instead of ID
    """
    try:
        # Find tasks matching the criteria
        matching_tasks = _find_tasks_by_criteria(
            user_id=user_id,
            title=title,
            priority=priority,
            status=status,
            include_completed=True  # Include completed tasks for updates
        )

        if not matching_tasks and title:
            # If no exact match, try fuzzy matching for title and description
            all_tasks_result = TaskOperationsService.list_tasks(
                user_id=user_id,
                include_completed=True
            )

            if all_tasks_result.get("status") == "success":
                all_tasks = all_tasks_result.get("tasks", [])

                # Use fuzzy matching to find tasks with similar titles or descriptions
                titles = [task.get("title", "") for task in all_tasks]
                descriptions = [task.get("description", "") for task in all_tasks]
                
                # Search in titles
                close_matches = get_close_matches(title.lower(),
                                               [t.lower() for t in titles],
                                               n=5, cutoff=0.3)
                
                # Also search in descriptions if title search didn't find anything
                if not close_matches:
                    close_matches = get_close_matches(title.lower(),
                                                   [d.lower() for d in descriptions if d],
                                                   n=5, cutoff=0.3)

                if close_matches:
                    # Find the tasks that correspond to the close matches (search both title and description)
                    for task in all_tasks:
                        task_matched = (
                            task.get("title", "").lower() in [match.lower() for match in close_matches] or
                            task.get("description", "").lower() in [match.lower() for match in close_matches]
                        )
                        if task_matched:
                            # Check if it's not already in matching_tasks to avoid duplicates
                            if not any(t['id'] == task['id'] for t in matching_tasks):
                                matching_tasks.append(task)

        if not matching_tasks:
            return {
                "status": "error",
                "message": f"No tasks found matching the criteria: title='{title}', priority='{priority}', status='{status}'"
            }

        # CRITICAL: Prevent updating multiple tasks without explicit confirmation
        if len(matching_tasks) > 1:
            task_list = "\n".join([f"  • {t.get('title', 'Unknown')} (ID: {t.get('id', 'N/A')})" 
                                   for t in matching_tasks])
            return {
                "status": "ambiguous",
                "message": f"Found {len(matching_tasks)} matching tasks. Please clarify which one(s) to update:\n{task_list}",
                "tasks": matching_tasks
            }

        # Update the single matching task
        updated_count = 0
        failed_tasks = []

        for task in matching_tasks:
            result = TaskOperationsService.update_task(
                task_id=task["id"],
                title=new_title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date,
                reminder_time=reminder_time,
                tags=tags,
                recurrence_pattern=recurrence_pattern,
                parent_task_id=parent_task_id
            )

            if result.get("status") == "success":
                updated_count += 1
            else:
                failed_tasks.append(task.get("title", "Unknown Task"))

        if updated_count > 0:
            return {
                "status": "success",
                "message": f"Successfully updated {updated_count} task(s)",
                "updated_tasks_count": updated_count,
                "failed_tasks": failed_tasks
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to update any tasks. Errors occurred with: {', '.join(failed_tasks) if failed_tasks else 'Unknown error'}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to update tasks by description: {str(e)}"
        }


def delete_tasks_by_description(title: str = None, priority: str = None,
                              user_id: str = "", status: str = None) -> Dict:
    """
    Delete tasks based on description criteria instead of ID
    """
    try:
        # Find tasks matching the criteria
        matching_tasks = _find_tasks_by_criteria(
            user_id=user_id,
            title=title,
            priority=priority,
            status=status,
            include_completed=True  # Include completed tasks for deletion
        )

        if not matching_tasks and title:
            # If no exact match, try fuzzy matching for title and description
            all_tasks_result = TaskOperationsService.list_tasks(
                user_id=user_id,
                include_completed=True
            )

            if all_tasks_result.get("status") == "success":
                all_tasks = all_tasks_result.get("tasks", [])

                # Use fuzzy matching to find tasks with similar titles or descriptions
                titles = [task.get("title", "") for task in all_tasks]
                descriptions = [task.get("description", "") for task in all_tasks]
                
                # Search in titles
                close_matches = get_close_matches(title.lower(),
                                               [t.lower() for t in titles],
                                               n=3, cutoff=0.3)
                
                # Also search in descriptions if title search didn't find anything
                if not close_matches:
                    close_matches = get_close_matches(title.lower(),
                                                   [d.lower() for d in descriptions if d],
                                                   n=3, cutoff=0.3)

                if close_matches:
                    # Find the tasks that correspond to the close matches (search both title and description)
                    for task in all_tasks:
                        task_matched = (
                            task.get("title", "").lower() in [match.lower() for match in close_matches] or
                            task.get("description", "").lower() in [match.lower() for match in close_matches]
                        )
                        if task_matched:
                            # Check if it's not already in matching_tasks to avoid duplicates
                            if not any(t['id'] == task['id'] for t in matching_tasks):
                                matching_tasks.append(task)

        if not matching_tasks:
            return {
                "status": "error",
                "message": f"No tasks found matching the criteria: title='{title}', priority='{priority}', status='{status}'"
            }

        # CRITICAL: Prevent deleting multiple tasks without explicit confirmation
        if len(matching_tasks) > 1:
            task_list = "\n".join([f"  • {t.get('title', 'Unknown')} (ID: {t.get('id', 'N/A')})" 
                                   for t in matching_tasks])
            return {
                "status": "ambiguous",
                "message": f"Found {len(matching_tasks)} matching tasks. Please clarify which one(s) to delete:\n{task_list}",
                "tasks": matching_tasks
            }

        # Delete the single matching task
        deleted_count = 0
        failed_tasks = []

        for task in matching_tasks:
            result = TaskOperationsService.delete_task(task["id"])
            if result.get("status") == "success":
                deleted_count += 1
            else:
                failed_tasks.append(task.get("title", "Unknown Task"))

        if deleted_count > 0:
            return {
                "status": "success",
                "message": f"Successfully deleted {deleted_count} task(s)",
                "deleted_tasks_count": deleted_count,
                "failed_tasks": failed_tasks
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to delete any tasks. Errors occurred with: {', '.join(failed_tasks) if failed_tasks else 'Unknown error'}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete tasks by description: {str(e)}"
        }