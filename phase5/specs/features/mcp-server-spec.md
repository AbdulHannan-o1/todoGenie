# MCP Server Specification

## Overview

This document defines the MCP (Model Context Protocol) Server implementation using the **Official MCP SDK** as required by the hackathon specification.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP Server Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    MCP Server (Official SDK)                           │  │
│  │                                                                          │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Tool Registry                                  │  │  │
│  │  │                                                                  │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │  │
│  │  │  │ add_task    │  │ list_tasks  │  │ complete_   │              │  │  │
│  │  │  │             │  │             │  │ task        │              │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘              │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │  │
│  │  │  │ delete_task │  │ update_task │  │ get_task_   │              │  │  │
│  │  │  │             │  │             │  │ by_id       │              │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘              │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐                              │  │  │
│  │  │  │ get_child_  │  │ create_child│                              │  │  │
│  │  │  │ tasks       │  │ task        │                              │  │  │
│  │  │  └─────────────┘  └─────────────┘                              │  │  │
│  │  │  ┌─────────────┐                                                │  │  │
│  │  │  │ get_upcoming│                                                │  │  │
│  │  │  │ reminders   │                                                │  │  │
│  │  │  └─────────────┘                                                │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                               │                                         │  │
│  │                               ▼                                         │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Tool Implementations                           │  │  │
│  │  │  (todo_tools.py)                                                 │  │  │
│  │  │                                                                  │  │  │
│  │  │  - create_task_tool()                                            │  │  │
│  │  │  - list_tasks_tool()                                             │  │  │
│  │  │  - update_task_tool()                                            │  │  │
│  │  │  - delete_task_tool()                                            │  │  │
│  │  │  - complete_task_tool()                                          │  │  │
│  │  │  - get_task_by_id_tool()                                         │  │  │
│  │  │  - get_child_tasks_tool()                                        │  │  │
│  │  │  - create_child_task_tool()                                      │  │  │
│  │  │  - get_upcoming_reminders_tool()                                 │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                               │                                         │  │
│  │                               ▼                                         │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    TaskOperationsService                          │  │  │
│  │  │  (SQLModel + PostgreSQL)                                          │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                               │                                              │
│                               │ MCP Protocol (stdio/HTTP)                    │
│                               ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    MCP Client (OpenAI Agents SDK)                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MCP Server Implementation

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.tool_registry import ToolRegistry

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

# Create the MCP server instance
server = Server("todogenie-mcp-server")

# Register the tool registry
registry = ToolRegistry()

# Register all tools
registry.register_tool(Tool(
    name="add_task",
    description="Create a new task with optional tags, priority, due_date, reminders, recurrence, and hierarchical relationships",
    inputSchema={
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
))

# Register remaining tools...

# Set up the server
@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return registry.list_tools()

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Execute a tool with given arguments.

    Args:
        name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        List of TextContent with tool results
    """
    try:
        result = await registry.execute_tool(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": str(e)
            })
        )]

@server.list_resources()
async def list_resources() -> list:
    """Return list of available resources."""
    return []

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    raise ValueError(f"Resource not found: {uri}")
```

### 2. Tool Registry

```python
class ToolRegistry:
    """
    Registry for managing MCP tools.

    Handles tool registration, lookup, and execution.
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    async def execute_tool(self, name: str, arguments: dict) -> Dict[str, Any]:
        """
        Execute a tool.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        # Get the actual tool function from todo_tools.py
        tool_function = self._get_tool_function(name)

        # Execute the tool
        result = tool_function(**arguments)
        return result

    def _get_tool_function(self, name: str) -> Callable:
        """Get the actual Python function for a tool."""
        # Import all tool functions from todo_tools.py
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

        tool_functions = {
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

        return tool_functions.get(name)
```

### 3. Tool Implementations

```python
from src.services.task_operations import TaskOperationsService

def create_task_tool(
    title: str,
    description: Optional[str] = None,
    user_id: str = "",
    tags: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence_pattern: Optional[Dict] = None,
    parent_task_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task via MCP tool.

    Args:
        title: Task title (required)
        description: Task description (optional)
        user_id: User ID (required)
        tags: Comma-separated tags (optional)
        priority: Priority level (optional)
        due_date: ISO format due date (optional)
        reminder_time: ISO format reminder time (optional)
        recurrence_pattern: Recurrence pattern (optional)
        parent_task_id: Parent task ID (optional)

    Returns:
        Dict with status and task details
    """
    try:
        result = TaskOperationsService.create_task(
            title=title,
            description=description,
            user_id=user_id,
            tags=tags,
            priority=priority,
            due_date=due_date,
            reminder_time=reminder_time,
            recurrence_pattern=recurrence_pattern,
            parent_task_id=parent_task_id
        )

        if result.get("status") == "success":
            return {
                "status": "success",
                "task": result.get("task", {}),
                "message": "Task created successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to create task")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating task: {str(e)}"
        }

def list_tasks_tool(
    user_id: str = "",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List tasks for a user with optional filters.

    Args:
        user_id: User ID (required)
        status: Filter by status (pending/completed/all)
        priority: Filter by priority (high/medium/low)
        search: Search keywords in title/description

    Returns:
        List of task dictionaries
    """
    try:
        result = TaskOperationsService.list_tasks_with_filters(
            user_id=user_id,
            status=status,
            priority=priority,
            search=search
        )

        if result.get("status") == "success":
            return result.get("tasks", [])
        else:
            return []

    except Exception as e:
        return []

def complete_task_tool(
    task_id: str,
    completed: bool = True
) -> Dict[str, Any]:
    """
    Mark a task as complete or incomplete.

    Args:
        task_id: Task ID (required)
        completed: Whether to mark as complete (default: True)

    Returns:
        Dict with status and message
    """
    try:
        result = TaskOperationsService.complete_task(task_id, completed)

        if result.get("status") == "success":
            return {
                "status": "success",
                "message": "Task marked as complete" if completed else "Task marked as incomplete"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to update task")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating task: {str(e)}"
        }

def delete_task_tool(
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task by ID.

    Args:
        task_id: Task ID (required)

    Returns:
        Dict with status and message
    """
    try:
        result = TaskOperationsService.delete_task(task_id)

        if result.get("status") == "success":
            return {
                "status": "success",
                "message": "Task deleted successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to delete task")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting task: {str(e)}"
        }

def update_task_tool(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    tags: Optional[str] = None,
    recurrence_pattern: Optional[Dict] = None,
    parent_task_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        task_id: Task ID (required)
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
        due_date: New due date (optional)
        reminder_time: New reminder time (optional)
        tags: New tags (optional)
        recurrence_pattern: New recurrence pattern (optional)
        parent_task_id: New parent task ID (optional)

    Returns:
        Dict with status and message
    """
    try:
        result = TaskOperationsService.update_task(
            task_id=task_id,
            title=title,
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
            return {
                "status": "success",
                "message": "Task updated successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to update task")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating task: {str(e)}"
        }

def get_task_by_id_tool(
    task_id: str
) -> Dict[str, Any]:
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID (required)

    Returns:
        Dict with task details or error
    """
    try:
        result = TaskOperationsService.get_task_by_id(task_id)

        if result.get("status") == "success":
            return {
                "status": "success",
                "task": result.get("task", {})
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Task not found")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting task: {str(e)}"
        }

def get_child_tasks_tool(
    task_id: str
) -> List[Dict[str, Any]]:
    """
    Get all child tasks for a parent task.

    Args:
        task_id: Parent task ID (required)

    Returns:
        List of child task dictionaries
    """
    try:
        result = TaskOperationsService.get_child_tasks(task_id)

        if result.get("status") == "success":
            return result.get("tasks", [])
        else:
            return []

    except Exception as e:
        return []

def create_child_task_tool(
    parent_task_id: str,
    title: str,
    description: Optional[str] = None,
    user_id: str = "",
    tags: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence_pattern: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create a child task under a parent task.

    Args:
        parent_task_id: Parent task ID (required)
        title: Task title (required)
        description: Task description (optional)
        user_id: User ID (required)
        tags: Comma-separated tags (optional)
        priority: Priority level (optional)
        due_date: Due date (optional)
        reminder_time: Reminder time (optional)
        recurrence_pattern: Recurrence pattern (optional)

    Returns:
        Dict with status and task details
    """
    try:
        result = TaskOperationsService.create_child_task(
            parent_task_id=parent_task_id,
            title=title,
            description=description,
            user_id=user_id,
            tags=tags,
            priority=priority,
            due_date=due_date,
            reminder_time=reminder_time,
            recurrence_pattern=recurrence_pattern
        )

        if result.get("status") == "success":
            return {
                "status": "success",
                "task": result.get("task", {}),
                "message": "Child task created successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to create child task")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating child task: {str(e)}"
        }

def get_upcoming_reminders_tool(
    user_id: str,
    hours_ahead: int = 24
) -> List[Dict[str, Any]]:
    """
    Get upcoming reminders for a user.

    Args:
        user_id: User ID (required)
        hours_ahead: Number of hours ahead to check (default: 24)

    Returns:
        List of reminder dictionaries
    """
    try:
        result = TaskOperationsService.get_upcoming_reminders(user_id, hours_ahead)

        if result.get("status") == "success":
            return result.get("reminders", [])
        else:
            return []

    except Exception as e:
        return []
```

### 4. MCP Server Entry Point

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

async def main():
    """Main entry point for MCP server."""
    server = Server("todogenie-mcp-server")

    # Register all tools
    await registry.register_tools_from_module(
        module="src.services.mcp_server.todo_tools"
    )

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 5. Tool Schema Definitions

```python
# Complete tool schemas for MCP server

TOOL_SCHEMAS = {
    "add_task": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The task title"},
            "description": {"type": "string", "description": "The task description"},
            "user_id": {"type": "string", "description": "The user ID"},
            "tags": {"type": "string", "description": "Tags for the task"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "description": "Priority level"
            },
            "due_date": {"type": "string", "format": "date-time", "description": "Due date"},
            "reminder_time": {"type": "string", "format": "date-time", "description": "Reminder time"},
            "recurrence_pattern": {
                "type": "object",
                "properties": {
                    "frequency": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly", "yearly"],
                        "description": "Recurrence frequency"
                    },
                    "interval": {"type": "integer", "description": "Interval multiplier"},
                    "end_date": {"type": "string", "format": "date-time", "description": "When to stop"}
                }
            },
            "parent_task_id": {"type": "string", "description": "Parent task ID"}
        },
        "required": ["title", "user_id"]
    },
    "list_tasks": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The user ID"},
            "status": {
                "type": "string",
                "enum": ["pending", "completed", "all"],
                "description": "Filter by status"
            },
            "priority": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Filter by priority"
            },
            "search": {"type": "string", "description": "Search keywords"}
        },
        "required": ["user_id"]
    },
    "update_task": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The task ID"},
            "title": {"type": "string", "description": "New title"},
            "description": {"type": "string", "description": "New description"},
            "status": {"type": "string", "description": "New status"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "description": "New priority"
            },
            "due_date": {"type": "string", "format": "date-time", "description": "New due date"},
            "reminder_time": {"type": "string", "format": "date-time", "description": "New reminder time"},
            "tags": {"type": "string", "description": "New tags"},
            "recurrence_pattern": {
                "type": "object",
                "properties": {
                    "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly"]},
                    "interval": {"type": "integer"},
                    "end_date": {"type": "string", "format": "date-time"}
                }
            },
            "parent_task_id": {"type": "string", "description": "New parent task ID"}
        },
        "required": ["task_id"]
    },
    "complete_task": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The task ID"},
            "completed": {"type": "boolean", "default": True, "description": "Mark as complete"}
        },
        "required": ["task_id"]
    },
    "delete_task": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The task ID"}
        },
        "required": ["task_id"]
    },
    "get_task_by_id": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The task ID"}
        },
        "required": ["task_id"]
    },
    "get_child_tasks": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The parent task ID"}
        },
        "required": ["task_id"]
    },
    "create_child_task": {
        "type": "object",
        "properties": {
            "parent_task_id": {"type": "string", "description": "The parent task ID"},
            "title": {"type": "string", "description": "The task title"},
            "description": {"type": "string", "description": "The task description"},
            "user_id": {"type": "string", "description": "The user ID"},
            "tags": {"type": "string", "description": "Tags for the task"},
            "priority": {"type": "string", "description": "Priority level"},
            "due_date": {"type": "string", "format": "date-time", "description": "Due date"},
            "reminder_time": {"type": "string", "format": "date-time", "description": "Reminder time"},
            "recurrence_pattern": {
                "type": "object",
                "properties": {
                    "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "yearly"]},
                    "interval": {"type": "integer"},
                    "end_date": {"type": "string", "format": "date-time"}
                }
            }
        },
        "required": ["parent_task_id", "title", "user_id"]
    },
    "get_upcoming_reminders": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The user ID"},
            "hours_ahead": {"type": "integer", "default": 24, "description": "Hours ahead to check"}
        },
        "required": ["user_id"]
    }
}
```

## Running the MCP Server

### As Standalone Process

```bash
# Run MCP server with stdio
python -m src.services.mcp_server.main

# Run MCP server with HTTP (for testing)
python -m src.services.mcp_server.main --http
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.services.mcp_server.main"]
```

## Testing

### Manual Testing

```bash
# List available tools
python -m src.services.mcp_server.main --list-tools

# Call a tool (interactive)
python -m src.services.mcp_server.main --call-tool add_task '{"title": "Test", "user_id": "123"}'
```

### Automated Testing

```python
import pytest
from mcp.client import Client

@pytest.mark.asyncio
async def test_mcp_server_tools():
    """Test that MCP server exposes all expected tools."""
    async with Client("stdio://") as client:
        tools = await client.list_tools()

        expected_tools = [
            "add_task",
            "list_tasks",
            "update_task",
            "delete_task",
            "complete_task",
            "get_task_by_id",
            "get_child_tasks",
            "create_child_task",
            "get_upcoming_reminders"
        ]

        assert len(tools) == len(expected_tools)
        assert {tool.name for tool in tools} == set(expected_tools)

@pytest.mark.asyncio
async def test_add_task_tool():
    """Test the add_task tool."""
    async with Client("stdio://") as client:
        result = await client.call_tool(
            "add_task",
            {
                "title": "Test Task",
                "user_id": "test-user-123"
            }
        )

        assert result["status"] == "success"
        assert "Test Task" in result["task"]["title"]
```

## Error Handling

The MCP server must handle errors gracefully:

1. **Invalid tool name** - Return 404
2. **Invalid arguments** - Return 400 with validation errors
3. **Tool execution error** - Return 500 with error message
4. **Database errors** - Return 500 with sanitized error message

## References

- [Official MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
