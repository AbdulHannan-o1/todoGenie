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
    delete_task_tool, complete_task_tool
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
                    "description": "Create a new task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The task title"},
                            "description": {"type": "string", "description": "The task description"},
                            "user_id": {"type": "string", "description": "The user ID"}
                        },
                        "required": ["title", "user_id"]
                    }
                },
                {
                    "name": "list_tasks",
                    "description": "List all tasks for the user",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "The user ID"}
                        },
                        "required": ["user_id"]
                    }
                },
                {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to update"},
                            "title": {"type": "string", "description": "The new title"},
                            "description": {"type": "string", "description": "The new description"},
                            "status": {"type": "string", "description": "The new status"}
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
                    "description": "Mark a task as complete",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to complete"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"},
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
                        user_id=params.get("user_id", "")
                    )
                elif tool_name == "list_tasks":
                    result = list_tasks_tool(
                        user_id=params.get("user_id", "")
                    )
                elif tool_name == "update_task":
                    result = update_task_tool(
                        task_id=params.get("task_id"),
                        title=params.get("title"),
                        description=params.get("description"),
                        status=params.get("status")
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