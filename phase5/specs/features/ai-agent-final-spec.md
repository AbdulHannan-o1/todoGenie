# AI Agent Implementation Specification

## Current State vs Required State

| Component | Current State | Required State | Gap |
|-----------|---------------|----------------|-----|
| AI Framework | Raw `chat.completions.create()` | OpenAI Agents SDK (Agent + Runner) | ❌ Not implemented |
| Tool Routing | Direct function imports | MCP Client → MCP Server | ❌ Not implemented |
| MCP SDK | Custom FastAPI REST API | Official MCP SDK | ❌ Not implemented |
| State Management | In-memory conversation | Dapr State Store | ❌ Not implemented |
| Agent Pattern | Manual agentic loop | Agent + Runner pattern | ❌ Not implemented |

---

## Implementation Plan

### Phase 1: Install Dependencies

```bash
pip install openai mcp dapr-http-client
```

### Phase 2: Create MCP Client

Create `phase5/backend/src/services/ai_agent/mcp_client.py`:

```python
from mcp import Client, StdioServerParameters
from typing import Dict, Any, List, Optional
import json

class MCPClient:
    """
    MCP Client for executing tools via the MCP server.

    Uses official MCP SDK to call tools defined in MCP server.
    """

    def __init__(self, server_command: str = "python", server_args: List[str] = None):
        """
        Initialize MCP Client.

        Args:
            server_command: Command to run the MCP server
            server_args: Arguments for the MCP server
        """
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args or ["-m", "src.services.mcp_server.main"],
            env=None
        )
        self.client: Optional[Client] = None

    async def connect(self) -> None:
        """Connect to the MCP server."""
        self.client = Client(self.server_params)
        await self.client.connect()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from MCP server."""
        if not self.client:
            await self.connect()
        tools = await self.client.list_tools()
        return [self._tool_to_dict(tool) for tool in tools]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool via MCP server.

        Args:
            name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self.client:
            await self.connect()

        result = await self.client.call_tool(name, arguments)
        return result.content[0].text

    async def close(self) -> None:
        """Close the MCP client connection."""
        if self.client:
            await self.client.close()

    def _tool_to_dict(self, tool) -> Dict[str, Any]:
        """Convert MCP tool to dictionary."""
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        }
```

### Phase 3: Create AIAgentRunner

Create `phase5/backend/src/services/ai_agent/ai_agent_runner.py`:

```python
from openai import OpenAI, Agent, Runner
from typing import Dict, Any, Optional
import os

from .mcp_client import MCPClient

class AIAgentRunner:
    """
    AI Agent orchestrator using OpenAI Agents SDK.

    Uses Agent + Runner pattern with MCP Client for tool execution.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the AI Agent Runner.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.mcp_client = MCPClient()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create and configure the AI Agent using OpenAI Agents SDK.

        Returns:
            Configured Agent instance
        """
        client = OpenAI(api_key=self.openai_api_key)

        agent = Agent(
            client=client,
            instructions=self._get_system_prompt(),
            model="gpt-4o-mini",
            name="task-manager-agent",
            instructions_prefix="""
            You are a task management assistant.
            Use the available tools to help users manage their tasks.
            """,
            instructions_suffix="""
            Always respond in a friendly, conversational tone.
            """,
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

        AVAILABLE TOOLS (via MCP):
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
        """
        try:
            # Initialize MCP client
            await self.mcp_client.connect()

            # Get available tools
            tools = await self.mcp_client.list_tools()

            # Create Runner with context
            runner = Runner(agent=self.agent, async_mode=True)

            # Execute the agent
            result = await runner.run(
                message=message,
                context={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "tools": tools
                }
            )

            # Get tool results
            tool_results = []
            if hasattr(result, 'tool_results') and result.tool_results:
                for tool_result in result.tool_results:
                    tool_results.append({
                        "tool": tool_result.get("name", "unknown"),
                        "result": tool_result.get("content", {})
                    })

            await self.mcp_client.close()

            return {
                "response": result.output,
                "tool_results": tool_results,
                "conversation_id": conversation_id
            }

        except Exception as e:
            if self.mcp_client.client:
                await self.mcp_client.close()
            raise

    async def close(self) -> None:
        """Close the MCP client connection."""
        await self.mcp_client.close()
```

### Phase 4: Update Chat API Endpoint

Update `phase5/backend/src/routes/chat.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from src.services.ai_agent.ai_agent_runner import AIAgentRunner

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    tool_results: List[Dict[str, Any]]
    conversation_id: str
    success: bool

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest
):
    """
    Process a user message through the AI agent.

    This endpoint uses OpenAI Agents SDK with Agent + Runner pattern.
    """
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4()}"

    try:
        # Initialize AI Agent Runner
        agent_runner = AIAgentRunner()

        # Process message through AI agent
        result = await agent_runner.chat(
            user_id=user_id,
            message=request.message,
            conversation_id=conversation_id
        )

        return ChatResponse(
            response=result["response"],
            tool_results=result["tool_results"],
            conversation_id=conversation_id,
            success=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )
```

### Phase 5: Update MCP Server Entry Point

Create `phase5/backend/src/services/mcp_server/main.py`:

```python
"""
MCP Server entry point using official MCP SDK.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.tool_registry import ToolRegistry

from .todo_tools import (
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

# Register all tools from todo_tools.py
def register_all_tools():
    """Register all tool functions from todo_tools.py"""
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

    for name, func in tool_functions.items():
        registry.register_tool(Tool(
            name=name,
            description=func.__doc__,
            inputSchema=func.__annotations__.get('return', {})
        ))

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
        tool = registry.get_tool(name)
        if not tool:
            return [TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"Tool not found: {name}"})
            )]

        # Execute the actual tool function
        result = tool(arguments)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
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

async def main():
    """Main entry point for MCP server."""
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

---

## Testing

### Test MCP Client

```python
import asyncio
from src.services.ai_agent.mcp_client import MCPClient

async def test_mcp_client():
    client = MCPClient()
    await client.connect()

    # List tools
    tools = await client.list_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")

    # Call a tool
    result = await client.call_tool("add_task", {
        "title": "Test Task",
        "user_id": "test-user"
    })
    print(f"Result: {result}")

    await client.close()

asyncio.run(test_mcp_client())
```

### Test AI Agent Runner

```python
import asyncio
from src.services.ai_agent.ai_agent_runner import AIAgentRunner

async def test_agent():
    runner = AIAgentRunner()

    result = await runner.chat(
        user_id="test-user",
        message="Add a task called Buy groceries"
    )

    print(f"Response: {result['response']}")
    print(f"Tool Results: {result['tool_results']}")

    await runner.close()

asyncio.run(test_agent())
```

---

## Migration Checklist

- [ ] Install `openai`, `mcp`, `dapr-http-client` packages
- [ ] Create `mcp_client.py`
- [ ] Create `ai_agent_runner.py`
- [ ] Create `mcp_server/main.py`
- [ ] Update `chat.py` endpoint
- [ ] Update `__init__.py` to export new components
- [ ] Test MCP client connection
- [ ] Test AI agent with simple message
- [ ] Test complete workflow
- [ ] Update documentation
