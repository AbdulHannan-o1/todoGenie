# AI Agent SDK Implementation Specification

## Overview

This specification defines the AI Agent implementation using **OpenAI Agents SDK** exactly as shown in the reference code, with OpenAI-compatible models.

## Reference Pattern

```python
from agents import Agent, Runner, function_tool, AsyncOpenAI, set_default_openai_client, set_default_openai_api

@function_tool
def add_task(title: str, user_id: str) -> dict:
    """Create a new task"""
    return {"status": "success", "task_id": "123"}

agent = Agent(
    name="TaskManager",
    instructions="You are a helpful task manager",
    model="gpt-4o-mini",
    tools=[add_task]
)

result = Runner.run_sync(agent, "Create a task called 'Buy groceries'")
print(result.final_output)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenAI Agents SDK Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ChatKit Frontend                                                           │
│       │                                                                     │
│       │ POST /api/{user_id}/chat                                            │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Chat Endpoint                             │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │           AIAgentRunner                                      │    │   │
│  │  │                                                              │    │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │    │   │
│  │  │  │           Agent (OpenAI Agents SDK)                  │   │    │   │
│  │  │  │                                                      │   │    │   │
│  │  │  │  @function_tool decorators for all tools           │   │    │   │
│  │  │  │  - add_task                                         │   │    │   │
│  │  │  │  - list_tasks                                       │   │    │   │
│  │  │  │  - update_task                                      │   │    │   │
│  │  │  │  - complete_task                                    │   │    │   │
│  │  │  │  - delete_task                                      │   │    │   │
│  │  │  │  - get_task_by_id                                   │   │    │   │
│  │  │  │  - get_child_tasks                                  │   │    │   │
│  │  │  │  - create_child_task                                │   │    │   │
│  │  │  │  - get_upcoming_reminders                           │   │    │   │
│  │  │  └─────────────────────────────────────────────────────┘   │    │   │
│  │  │                        │                                    │    │   │
│  │  │                        ▼                                    │    │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │    │   │
│  │  │  │           Runner.run_sync()                         │   │    │   │
│  │  │  │           (Handles agentic loop automatically)      │   │    │   │
│  │  │  └─────────────────────────────────────────────────────┘   │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                                              │    │   │
│  │  ┌─────────────────────────────────────────────────────┐   │    │   │
│  │  │           MCP Tool Server                            │   │    │   │
│  │  │           (HTTP-based tool execution)                │   │    │   │
│  │  └─────────────────────────────────────────────────────┘   │    │   │
│  └────────────────────────────────────────────────────────────┘    │   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AIAgentRunner

```python
"""
AI Agent runner using OpenAI Agents SDK with function_tool decorators.
"""
from agents import Agent, Runner, function_tool
from agents.openai import AsyncOpenAI
import os

# Set default OpenAI API type
set_default_openai_api("chat_completions")

# Create OpenAI-compatible client
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
set_default_openai_client(openai_client)


class AIAgentRunner:
    """
    AI Agent runner using OpenAI Agents SDK with Agent + Runner pattern.

    Uses @function_tool decorators for all tool definitions.
    Uses Runner.run_sync() for synchronous execution.
    """

    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the AI Agent Runner.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            model: Model to use (chat_completion, response, or assistant)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        # Set default OpenAI API type
        set_default_openai_api("chat_completions")

        # Create OpenAI-compatible client
        self.openai_client = AsyncOpenAI(
            api_key=self.openai_api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        set_default_openai_client(self.openai_client)

        # Create Agent with function_tool decorators
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create Agent using @function_tool decorators.

        Returns:
            Configured Agent instance
        """
        agent = Agent(
            name="TaskManager",
            instructions=self._get_system_prompt(),
            model=self.model,
            tools=[
                self.add_task,
                self.list_tasks,
                self.update_task,
                self.complete_task,
                self.delete_task,
                self.get_task_by_id,
                self.get_child_tasks,
                self.create_child_task,
                self.get_upcoming_reminders,
            ]
        )
        return agent

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent.

        Returns:
            System prompt as string
        """
        return """
        You are a friendly task manager assistant that helps users manage their tasks.

        YOUR CAPABILITIES:
        - Create new tasks with title, description, priority, due date, reminders
        - List all tasks with filtering (status, priority, search)
        - Update existing tasks by ID or by description
        - Mark tasks as complete by ID or by description
        - Delete tasks by ID or by description

        TOOL SELECTION RULES:
        - When user mentions task by NAME/DESCRIPTION (not ID), use description-based tools
        - When user mentions task by NUMBER/ID, use ID-based tools
        - NEVER complete multiple tasks unless user EXPLICITLY mentions multiple tasks

        CRITICAL RULES:
        - If multiple tasks match description, ask user to clarify which one
        - Recognize context from conversation to identify specific task
        - Be warm and conversational

        AVAILABLE TOOLS:
        - add_task: Create a new task
        - list_tasks: List all tasks with filters
        - update_task: Update task by ID
        - complete_task: Mark task complete by ID
        - delete_task: Delete task by ID
        - get_task_by_id: Get task details
        - get_child_tasks: Get sub-tasks of a parent
        - create_child_task: Create a sub-task
        - get_upcoming_reminders: Get reminder notifications
        """

    # Tool functions using @function_tool decorator
    # These will be automatically registered with the Agent

    @function_tool
    def add_task(self, title: str, user_id: str, description: Optional[str] = None,
                 priority: Optional[str] = None, due_date: Optional[str] = None,
                 reminder_time: Optional[str] = None, tags: Optional[str] = None) -> dict:
        """
        Create a new task.

        Args:
            title: Task title (required)
            user_id: User ID (required)
            description: Optional task description
            priority: Optional priority level
            due_date: Optional due date
            reminder_time: Optional reminder time
            tags: Optional comma-separated tags

        Returns:
            Task creation result
        """
        # Call MCP server to execute the task creation
        result = await self.mcp_client.call_tool("add_task", {
            "title": title,
            "user_id": user_id,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "reminder_time": reminder_time,
            "tags": tags
        })
        return result

    @function_tool
    def list_tasks(self, user_id: str, status: Optional[str] = None,
                   priority: Optional[str] = None, search: Optional[str] = None) -> dict:
        """
        List all tasks with filters.

        Args:
            user_id: User ID (required)
            status: Optional filter by status
            priority: Optional filter by priority
            search: Optional search term

        Returns:
            List of tasks
        """
        result = await self.mcp_client.call_tool("list_tasks", {
            "user_id": user_id,
            "status": status,
            "priority": priority,
            "search": search
        })
        return result

    @function_tool
    def update_task(self, task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None, status: Optional[str] = None,
                    priority: Optional[str] = None, due_date: Optional[str] = None) -> dict:
        """
        Update a task by ID.

        Args:
            task_id: Task ID (required)
            title: Optional new title
            description: Optional new description
            status: Optional new status
            priority: Optional new priority
            due_date: Optional new due date

        Returns:
            Update result
        """
        result = await self.mcp_client.call_tool("update_task", {
            "task_id": task_id,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "due_date": due_date
        })
        return result

    @function_tool
    def complete_task(self, task_id: str, completed: bool = True) -> dict:
        """
        Mark a task as complete by ID.

        Args:
            task_id: Task ID (required)
            completed: Whether to mark as complete (default: True)

        Returns:
            Completion result
        """
        result = await self.mcp_client.call_tool("complete_task", {
            "task_id": task_id,
            "completed": completed
        })
        return result

    @function_tool
    def delete_task(self, task_id: str) -> dict:
        """
        Delete a task by ID.

        Args:
            task_id: Task ID (required)

        Returns:
            Deletion result
        """
        result = await self.mcp_client.call_tool("delete_task", {
            "task_id": task_id
        })
        return result

    @function_tool
    def get_task_by_id(self, task_id: str) -> dict:
        """
        Get a task by ID.

        Args:
            task_id: Task ID (required)

        Returns:
            Task details
        """
        result = await self.mcp_client.call_tool("get_task_by_id", {
            "task_id": task_id
        })
        return result

    @function_tool
    def get_child_tasks(self, task_id: str) -> dict:
        """
        Get sub-tasks of a parent task.

        Args:
            task_id: Parent task ID (required)

        Returns:
            List of child tasks
        """
        result = await self.mcp_client.call_tool("get_child_tasks", {
            "task_id": task_id
        })
        return result

    @function_tool
    def create_child_task(self, parent_task_id: str, title: str, user_id: str,
                         description: Optional[str] = None, priority: Optional[str] = None,
                         due_date: Optional[str] = None) -> dict:
        """
        Create a sub-task under a parent task.

        Args:
            parent_task_id: Parent task ID (required)
            title: Task title (required)
            user_id: User ID (required)
            description: Optional description
            priority: Optional priority
            due_date: Optional due date

        Returns:
            Created task
        """
        result = await self.mcp_client.call_tool("create_child_task", {
            "parent_task_id": parent_task_id,
            "title": title,
            "user_id": user_id,
            "description": description,
            "priority": priority,
            "due_date": due_date
        })
        return result

    @function_tool
    def get_upcoming_reminders(self, user_id: str, hours_ahead: int = 24) -> dict:
        """
        Get upcoming reminders for a user.

        Args:
            user_id: User ID (required)
            hours_ahead: Hours ahead to check (default: 24)

        Returns:
            List of upcoming reminders
        """
        result = await self.mcp_client.call_tool("get_upcoming_reminders", {
            "user_id": user_id,
            "hours_ahead": hours_ahead
        })
        return result

    async def chat(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message through the AI agent.

        Args:
            user_id: User identifier
            message: User input message
            conversation_id: Optional conversation ID for stateful chat

        Returns:
            Dict with 'response' and 'tool_results'

        Raises:
            AIAgentError: If agent execution fails
        """
        try:
            # Initialize MCP client
            await self.mcp_client.connect()

            # Use Runner.run_sync() for synchronous execution
            # Agent handles tool calling automatically via @function_tool
            result = Runner.run_sync(
                self.agent,
                message
            )

            await self.mcp_client.close()

            return {
                "response": result.final_output,
                "tool_results": result.tool_results or [],
                "conversation_id": conversation_id
            }

        except Exception as e:
            await self.mcp_client.close()
            raise AIAgentError(f"Agent execution failed: {e}")
```

### 2. MCP Client

```python
"""
MCP Client for executing tools via the MCP server.

Uses httpx AsyncClient to call HTTP endpoints.
"""
import httpx
from typing import Dict, Any, List, Optional


class MCPClient:
    """
    MCP Client for executing tools via the MCP server.
    """

    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize MCP Client.

        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self._http_client: Optional[httpx.AsyncClient] = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to the MCP server by initializing HTTP client."""
        if self._connected:
            return

        try:
            self._http_client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
            # Test connection
            await self.list_tools()
            self._connected = True
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MCP server at {self.base_url}: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from MCP server."""
        if not self._connected:
            await self.connect()

        if not self._http_client:
            raise RuntimeError("MCP client not initialized")

        try:
            response = await self._http_client.get("/tools")
            response.raise_for_status()
            data = response.json()
            return data.get("tools", [])
        except Exception as e:
            raise RuntimeError(f"Failed to list tools: {e}")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool via MCP server.

        Args:
            name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self._connected:
            await self.connect()

        if not self._http_client:
            raise RuntimeError("MCP client not initialized")

        try:
            response = await self._http_client.post(f"/tools/{name}", json=arguments)
            response.raise_for_status()
            data = response.json()
            return data.get("result", {})
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Tool execution failed: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to call tool '{name}': {e}")

    async def close(self) -> None:
        """Close the MCP client connection."""
        if self._http_client:
            try:
                await self._http_client.aclose()
            except Exception:
                pass
            finally:
                self._http_client = None
                self._connected = False

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
```

### 3. Tool Server (MCP Server)

```python
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
    version="1.0.0",
    description="MCP Tool Server for AI Agent - HTTP based implementation"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "TodoGenie Tool Server",
        "version": "1.0.0",
        "endpoints": {
            "/tools": "List all available tools",
            "/tools/{tool_name}": "Execute a tool"
        },
        "tools_count": 9
    }

@app.get("/tools")
async def list_tools():
    """
    List all available tools.

    Returns tool definitions compatible with OpenAI Agents SDK.
    """
    tools = get_tool_definitions()
    return {
        "tools": tools
    }

@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Execute a specific tool.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        Tool execution result
    """
    if tool_name not in tool_functions:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    try:
        result = await tool_functions[tool_name](**arguments)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

## Key Differences from Current Implementation

### Current Implementation (Raw Chat Completions API)
```python
# Manual tool definitions
tools = [{"type": "function", "function": {...}}]

# Manual agentic loop
for iteration in range(max_iterations):
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=self.tools,
        tool_choice="auto",
    )
    # ... manual tool calling and loop
```

### New Implementation (OpenAI Agents SDK)
```python
# @function_tool decorators
@function_tool
def add_task(title: str, user_id: str) -> dict:
    """Create a new task"""
    return {"status": "success"}

# Agent handles everything automatically
agent = Agent(
    name="TaskManager",
    instructions="...",
    model="gpt-4o-mini",
    tools=[add_task, list_tasks, ...]
)

# Runner handles agentic loop automatically
result = Runner.run_sync(agent, "Create a task called 'Buy groceries'")
```

## Model Types

The OpenAI Agents SDK supports three model types:

1. **chat_completion** (default): Standard chat model for conversational AI
2. **response**: Specialized for single-step responses
3. **assistant**: For assistant-like interactions with memory

```python
# Example with different model types
agent_chat = Agent(
    name="ChatBot",
    model="gpt-4o-mini",  # chat_completion type
    tools=[...]
)

agent_response = Agent(
    name="ResponseBot",
    model="gpt-4o-mini",  # response type
    tools=[...]
)

agent_assistant = Agent(
    name="AssistantBot",
    model="gpt-4o-mini",  # assistant type
    tools=[...]
)
```

## Dependencies

```txt
openai-agents>=0.0.1
httpx>=0.27.0
fastapi>=0.100.0
```

## Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional, for custom endpoints

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001
```
