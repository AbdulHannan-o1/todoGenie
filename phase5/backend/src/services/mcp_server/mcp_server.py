"""
MCP Server implementation for AI chatbot
"""
import asyncio
import json
from typing import Dict, Any, List
from fastapi import FastAPI
import uvicorn
from .todo_tools import (
    create_task_tool, list_tasks_tool, update_task_tool,
    delete_task_tool, complete_task_tool, get_child_tasks_tool,
    create_child_task_tool, get_upcoming_reminders_tool, get_task_by_id_tool
)


class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="TodoGenie MCP Server")
        self._setup_routes()
        self.server_instance = None

    def _setup_routes(self):
        """Setup MCP server routes for AI tools"""

        @self.app.get("/tools")
        async def get_tools() -> List[Dict]:
            """Return list of available tools in MCP format"""
            return [
                {
                    "name": "create_task",
                    "description": "Create a new task with optional tags, priority, due_date, reminders, recurrence, and hierarchical relationships",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The task title"},
                            "description": {"type": "string", "description": "The task description"},
                            "user_id": {"type": "string", "description": "The user ID"},
                            "tags": {"type": "string", "description": "Tags for the task"},
                            "priority": {"type": "string", "description": "Priority level (low, medium, high, urgent)"},
                            "due_date": {"type": "string", "description": "Due date in ISO format"},
                            "reminder_time": {"type": "string", "description": "Reminder time in ISO format"},
                            "recurrence_pattern": {"type": "object", "description": "Recurrence pattern with frequency and interval"},
                            "parent_task_id": {"type": "string", "description": "Parent task ID for hierarchical tasks"}
                        },
                        "required": ["title", "user_id"]
                    }
                },
                {
                    "name": "list_tasks",
                    "description": "List all tasks for the user with optional filters",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user ID"},
                            "include_completed": {"type": "boolean", "description": "Include completed tasks (default: true)"},
                            "priority_filter": {"type": "string", "description": "Filter by priority"},
                            "due_date_start": {"type": "string", "description": "Filter by start date in ISO format"},
                            "due_date_end": {"type": "string", "description": "Filter by end date in ISO format"}
                        },
                        "required": ["user_id"]
                    }
                },
                {
                    "name": "update_task",
                    "description": "Update an existing task with advanced features",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to update"},
                            "title": {"type": "string", "description": "The new title"},
                            "description": {"type": "string", "description": "The new description"},
                            "status": {"type": "string", "description": "The new status"},
                            "priority": {"type": "string", "description": "Priority level (low, medium, high, urgent)"},
                            "due_date": {"type": "string", "description": "Due date in ISO format"},
                            "reminder_time": {"type": "string", "description": "Reminder time in ISO format"},
                            "tags": {"type": "string", "description": "Tags for the task"},
                            "recurrence_pattern": {"type": "object", "description": "Recurrence pattern with frequency and interval"},
                            "parent_task_id": {"type": "string", "description": "Parent task ID for hierarchical tasks"}
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to delete"},
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "complete_task",
                    "description": "Mark a task as complete or incomplete",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to complete"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"},
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "get_child_tasks",
                    "description": "Get all child tasks for a parent task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the parent task"},
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "create_child_task",
                    "description": "Create a child task under a parent task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "parent_task_id": {"type": "string", "description": "The ID of the parent task"},
                            "title": {"type": "string", "description": "The task title"},
                            "description": {"type": "string", "description": "The task description"},
                            "user_id": {"type": "string", "description": "The user ID"},
                            "tags": {"type": "string", "description": "Tags for the task"},
                            "priority": {"type": "string", "description": "Priority level (low, medium, high, urgent)"},
                            "due_date": {"type": "string", "description": "Due date in ISO format"},
                            "reminder_time": {"type": "string", "description": "Reminder time in ISO format"},
                            "recurrence_pattern": {"type": "object", "description": "Recurrence pattern with frequency and interval"}
                        },
                        "required": ["parent_task_id", "title"]
                    }
                },
                {
                    "name": "get_upcoming_reminders",
                    "description": "Get upcoming reminders for a user",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user ID"},
                            "hours_ahead": {"type": "integer", "description": "Number of hours ahead to check for reminders (default: 24)"}
                        },
                        "required": ["user_id"]
                    }
                },
                {
                    "name": "get_task_by_id",
                    "description": "Get a specific task by ID",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to retrieve"},
                        },
                        "required": ["task_id"]
                    }
                }
            ]

        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, params: Dict) -> Dict:
            """Execute a specific tool with given parameters"""
            try:
                if tool_name == "create_task":
                    result = create_task_tool(
                        title=params.get("title"),
                        description=params.get("description"),
                        user_id=params.get("user_id", ""),
                        tags=params.get("tags"),
                        priority=params.get("priority"),
                        due_date=params.get("due_date"),
                        reminder_time=params.get("reminder_time"),
                        recurrence_pattern=params.get("recurrence_pattern"),
                        parent_task_id=params.get("parent_task_id")
                    )
                elif tool_name == "list_tasks":
                    result = list_tasks_tool(
                        user_id=params.get("user_id", ""),
                        include_completed=params.get("include_completed", True),
                        priority_filter=params.get("priority_filter"),
                        due_date_start=params.get("due_date_start"),
                        due_date_end=params.get("due_date_end")
                    )
                elif tool_name == "update_task":
                    result = update_task_tool(
                        task_id=params.get("task_id"),
                        title=params.get("title"),
                        description=params.get("description"),
                        status=params.get("status"),
                        priority=params.get("priority"),
                        due_date=params.get("due_date"),
                        reminder_time=params.get("reminder_time"),
                        tags=params.get("tags"),
                        recurrence_pattern=params.get("recurrence_pattern"),
                        parent_task_id=params.get("parent_task_id")
                    )
                elif tool_name == "delete_task":
                    result = delete_task_tool(
                        task_id=params.get("task_id")
                    )
                elif tool_name == "complete_task":
                    result = complete_task_tool(
                        task_id=params.get("task_id"),
                        completed=params.get("completed", True)
                    )
                elif tool_name == "get_child_tasks":
                    result = get_child_tasks_tool(
                        task_id=params.get("task_id")
                    )
                elif tool_name == "create_child_task":
                    result = create_child_task_tool(
                        parent_task_id=params.get("parent_task_id"),
                        title=params.get("title"),
                        description=params.get("description"),
                        user_id=params.get("user_id", ""),
                        tags=params.get("tags"),
                        priority=params.get("priority"),
                        due_date=params.get("due_date"),
                        reminder_time=params.get("reminder_time"),
                        recurrence_pattern=params.get("recurrence_pattern")
                    )
                elif tool_name == "get_upcoming_reminders":
                    result = get_upcoming_reminders_tool(
                        user_id=params.get("user_id"),
                        hours_ahead=params.get("hours_ahead", 24)
                    )
                elif tool_name == "get_task_by_id":
                    result = get_task_by_id_tool(
                        task_id=params.get("task_id")
                    )
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown tool: {tool_name}"
                    }

                return {
                    "status": "success",
                    "result": result
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }

    async def start(self, port: int = 8001):
        """Start the MCP server"""
        import threading
        import time

        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        self.server_instance = uvicorn.Server(config)

        # Run the server in a separate thread
        server_thread = threading.Thread(target=self.server_instance.run)
        server_thread.daemon = True
        server_thread.start()

        # Give the server a moment to start
        time.sleep(1)
        print(f"MCP Server started on port {port}")

    async def stop(self):
        """Stop the MCP server"""
        if self.server_instance:
            self.server_instance.should_exit = True
            print("MCP Server stopping")


# Global MCP server instance
mcp_server = MCPServer()