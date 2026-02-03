"""
Tool integration module for the AI Agent service
Handles the definition and execution of available tools for the AI agent
"""

import json
from typing import Dict, Any, List
from src.services.mcp_server.todo_tools import (
    create_task_tool, list_tasks_tool, update_task_tool,
    delete_task_tool, complete_task_tool, update_tasks_by_description,
    delete_tasks_by_description, complete_task_by_description
)


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Define the tools available to the AI agent
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description"},
                        "priority": {"type": "string", "description": "Priority: low, medium, high, or urgent"},
                        "due_date": {"type": "string", "description": "Due date (ISO format)"},
                        "reminder_time": {"type": "string", "description": "Reminder time (ISO format)"},
                        "tags": {"type": "string", "description": "Tags (comma-separated)"},
                        "recurrence_pattern": {
                            "type": "object",
                            "description": "Recurrence pattern for recurring tasks",
                            "properties": {
                                "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly", "custom"], "description": "Recurrence frequency"},
                                "interval": {"type": "integer", "description": "Interval multiplier"},
                                "end_condition": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["never", "on_date", "after_occurrences"], "description": "When to stop recurrence"},
                                        "value": {"type": ["string", "integer"], "description": "Date string or occurrence count"}
                                    }
                                },
                                "exceptions": {"type": "array", "items": {"type": "string"}, "description": "Array of dates to skip in recurrence"}
                            }
                        },
                        "parent_task_id": {"type": "string", "description": "ID of parent task for hierarchical tasks"}
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The ID of the task to update"},
                        "title": {"type": "string", "description": "The new title"},
                        "description": {"type": "string", "description": "The new description"},
                        "status": {"type": "string", "description": "The new status"},
                        "priority": {"type": "string", "description": "Priority: low, medium, high, or urgent"},
                        "due_date": {"type": "string", "description": "Due date (ISO format)"},
                        "reminder_time": {"type": "string", "description": "Reminder time (ISO format)"},
                        "tags": {"type": "string", "description": "Tags (comma-separated)"},
                        "recurrence_pattern": {
                            "type": "object",
                            "description": "Recurrence pattern for recurring tasks",
                            "properties": {
                                "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly", "custom"], "description": "Recurrence frequency"},
                                "interval": {"type": "integer", "description": "Interval multiplier"},
                                "end_condition": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["never", "on_date", "after_occurrences"], "description": "When to stop recurrence"},
                                        "value": {"type": ["string", "integer"], "description": "Date string or occurrence count"}
                                    }
                                },
                                "exceptions": {"type": "array", "items": {"type": "string"}, "description": "Array of dates to skip in recurrence"}
                            }
                        },
                        "parent_task_id": {"type": "string", "description": "ID of parent task for hierarchical tasks"}
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_tasks_by_description",
                "description": "Update multiple tasks based on description criteria instead of requiring IDs. Useful for updating tasks by priority, partial title, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Partial title to match tasks (case-insensitive)"},
                        "priority": {"type": "string", "description": "Priority level to match (low, medium, high, urgent)"},
                        "status": {"type": "string", "description": "Status to match (pending, in progress, completed, etc.)"},
                        "user_id": {"type": "string", "description": "User ID to scope the search"},
                        "new_title": {"type": "string", "description": "New title for matched tasks"},
                        "description": {"type": "string", "description": "New description for matched tasks"},
                        "due_date": {"type": "string", "description": "New due date (ISO format)"},
                        "reminder_time": {"type": "string", "description": "New reminder time (ISO format)"},
                        "tags": {"type": "string", "description": "New tags (comma-separated)"},
                        "recurrence_pattern": {
                            "type": "object",
                            "description": "New recurrence pattern for recurring tasks",
                            "properties": {
                                "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly", "custom"], "description": "Recurrence frequency"},
                                "interval": {"type": "integer", "description": "Interval multiplier"},
                                "end_condition": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["never", "on_date", "after_occurrences"], "description": "When to stop recurrence"},
                                        "value": {"type": ["string", "integer"], "description": "Date string or occurrence count"}
                                    }
                                },
                                "exceptions": {"type": "array", "items": {"type": "string"}, "description": "Array of dates to skip in recurrence"}
                            }
                        },
                        "parent_task_id": {"type": "string", "description": "New parent task ID for matched tasks"}
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The ID of the task to delete"},
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_tasks_by_description",
                "description": "Delete multiple tasks based on description criteria instead of requiring IDs. Useful for deleting tasks by priority, partial title, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Partial title to match tasks (case-insensitive)"},
                        "priority": {"type": "string", "description": "Priority level to match (low, medium, high, urgent)"},
                        "status": {"type": "string", "description": "Status to match (pending, in progress, completed, etc.)"},
                        "user_id": {"type": "string", "description": "User ID to scope the search"}
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The ID of the task to complete"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"},
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task_by_description",
                "description": "Mark multiple tasks as complete based on description criteria instead of requiring IDs. Useful for completing tasks by priority, partial title, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Partial title to match tasks (case-insensitive)"},
                        "priority": {"type": "string", "description": "Priority level to match (low, medium, high, urgent)"},
                        "status": {"type": "string", "description": "Status to match (pending, in progress, completed, etc.)"},
                        "user_id": {"type": "string", "description": "User ID to scope the search"}
                    },
                },
            },
        }
    ]
    return tools


def execute_tool(function_name: str, function_args: Dict[str, Any], user_id: str):
    """
    Execute the appropriate tool function with error handling
    """
    # Execute the appropriate tool function with enhanced error handling
    # Handle functions that require user_id as a direct parameter
    if function_name == "create_task":
        # Create task expects user_id as a parameter
        result = create_task_tool(user_id=user_id, **function_args)
    elif function_name == "list_tasks":
        # List tasks expects user_id as a parameter
        result = list_tasks_tool(user_id=user_id)
    # Handle functions that don't require user_id as a parameter (they get user info from task_id)
    elif function_name == "update_task":
        # Update task doesn't expect user_id - it gets user info from the task itself
        # Remove user_id from function_args to avoid TypeError
        task_args = {k: v for k, v in function_args.items() if k != "user_id"}
        result = update_task_tool(**task_args)
    elif function_name == "delete_task":
        # Delete task doesn't expect user_id - it gets user info from the task itself
        task_args = {k: v for k, v in function_args.items() if k != "user_id"}
        result = delete_task_tool(**task_args)
    elif function_name == "complete_task":
        # Complete task doesn't expect user_id - it gets user info from the task itself
        task_args = {k: v for k, v in function_args.items() if k != "user_id"}
        result = complete_task_tool(**task_args)
    # Handle our new enhanced functions that require user_id
    elif function_name == "update_tasks_by_description":
        result = update_tasks_by_description(user_id=user_id, **function_args)
    elif function_name == "delete_tasks_by_description":
        result = delete_tasks_by_description(user_id=user_id, **function_args)
    elif function_name == "complete_task_by_description":
        result = complete_task_by_description(user_id=user_id, **function_args)
    else:
        result = {"status": "error", "message": f"Unknown function: {function_name}"}

    return result