"""
MCP Tool Server for AI Agent - HTTP based

This server provides task management tools that can be called by the AI Agent.
Tools are exposed via HTTP endpoints instead of MCP stdio protocol.
"""
import sys
from pathlib import Path
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.services.mcp_server.todo_tools import (
    create_task_tool,
    list_tasks_tool,
    update_task_tool,
    delete_task_tool,
    complete_task_tool,
    get_task_by_id_tool,
    get_child_tasks_tool,
    create_child_task_tool,
    get_upcoming_reminders_tool
)

# Create the tool server
app = FastAPI(
    title="TodoGenie Tool Server",
    description="HTTP-based tool server for task management",
    version="1.0.0"
)
# Set default_response_class for FastAPI compatibility
app.default_response_class = None
app.generate_unique_id_function = None
app.strict_content_type = None
# Monkey-patch for compatibility
if not hasattr(app, 'default_response_class'):
    app.default_response_class = None
if not hasattr(app, 'generate_unique_id_function'):
    app.generate_unique_id_function = None
if not hasattr(app, 'strict_content_type'):
    app.strict_content_type = None

# Export the app
__all__ = ['app']

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tool definitions for AI agent
def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return tool definitions in OpenAI API format."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "user_id": {"type": "string"},
                        "tags": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_date": {"type": "string"},
                        "reminder_time": {"type": "string"},
                        "recurrence_pattern": {"type": "object"},
                        "parent_task_id": {"type": "string"}
                    },
                    "required": ["title", "user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks with filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "status": {"type": "string"},
                        "priority": {"type": "string"},
                        "search": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_date": {"type": "string"},
                        "reminder_time": {"type": "string"},
                        "tags": {"type": "string"},
                        "recurrence_pattern": {"type": "object"},
                        "parent_task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "completed": {"type": "boolean", "default": True}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_task_by_id",
                "description": "Get a task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_child_tasks",
                "description": "Get sub-tasks of a parent task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_child_task",
                "description": "Create a sub-task under a parent task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parent_task_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "user_id": {"type": "string"},
                        "tags": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_date": {"type": "string"},
                        "reminder_time": {"type": "string"},
                        "recurrence_pattern": {"type": "object"}
                    },
                    "required": ["parent_task_id", "title", "user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_upcoming_reminders",
                "description": "Get upcoming reminders for a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "hours_ahead": {"type": "integer", "default": 24}
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]


# Store tool function references
TOOL_FUNCTIONS = {
    "add_task": create_task_tool,
    "list_tasks": list_tasks_tool,
    "update_task": update_task_tool,
    "delete_task": delete_task_tool,
    "complete_task": complete_task_tool,
    "get_task_by_id": get_task_by_id_tool,
    "get_child_tasks": get_child_tasks_tool,
    "create_child_task": create_child_task_tool,
    "get_upcoming_reminders": get_upcoming_reminders_tool,
}


@app.get("/tools")
async def list_tools():
    """List all available tools in OpenAI API format."""
    return {
        "tools": get_tool_definitions()
    }


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    """
    Execute a specific tool with given parameters.

    Args:
        tool_name: Name of the tool to execute
        params: Tool arguments (user_id is extracted from query param if not in params)

    Returns:
        Tool execution result
    """
    try:
        # Get the tool function
        tool_func = TOOL_FUNCTIONS.get(tool_name)
        if not tool_func:
            raise HTTPException(
                status_code=404,
                detail=f"Tool not found: {tool_name}"
            )

        # Execute the tool
        result = tool_func(**params)

        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "TodoGenie Tool Server",
        "version": "1.0.0",
        "endpoints": {
            "/tools": "List all available tools",
            "/tools/{tool_name}": "Execute a tool"
        },
        "tools_count": len(TOOL_FUNCTIONS)
    }


# For backward compatibility with stdio-style entry point
async def main():
    """Entry point for HTTP server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
