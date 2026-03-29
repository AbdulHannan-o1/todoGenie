# AI Agent Architecture Specification

## Overview

This document defines the AI Agent implementation using **OpenAI Agents SDK** with **Agent + Runner** pattern as required by the hackathon specification.

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
│  │  │           AIAgentRunner (Agent + Runner)                     │    │   │
│  │  │                                                              │    │   │
│  │  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │    │   │
│  │  │  │   Agent      │───▶│   Runner     │───▶│  MCP Client  │   │    │   │
│  │  │  │              │    │              │    │              │   │    │   │
│  │  │  │  System      │    │  Agentic     │    │  HTTP Client │   │    │   │
│  │  │  │  Prompt      │    │  Loop        │    │              │   │    │   │
│  │  │  └──────────────┘    └──────────────┘    └──────┬───────┘   │    │   │
│  │                                                   │            │    │   │
│  │                                                   ▼            │    │   │
│  │                                      ┌──────────────────┐       │    │   │
│  │                                      │   MCP Server     │       │    │   │
│  │                                      │   (Official SDK) │       │    │   │
│  │                                      └────────┬─────────┘       │    │   │
│  │                                               │                 │    │   │
│  │                                               ▼                 │    │   │
│  │                                      ┌──────────────────┐       │    │   │
│  │                                      │   Tool Functions │       │    │   │
│  │                                      │  (add_task,      │       │    │   │
│  │                                      │   list_tasks,    │       │    │   │
│  │                                      │   complete_task, │       │    │   │
│  │                                      │   delete_task,   │       │    │   │
│  │                                      │   update_task)   │       │    │   │
│  │                                      └────────┬─────────┘       │    │   │
│  │                                               │                 │    │   │
│  └───────────────────────────────────────────────┼─────────────────┘    │   │
│                                                   │                     │   │
│                                                   ▼                     │   │
│  ┌───────────────────────────────────────────────┼─────────────────┐    │   │
│  │                                               ▼                 │    │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │   │
│  │  │              Dapr State Store (PostgreSQL)               │   │    │   │
│  │  │  - conversations (user_id, messages, metadata)           │   │    │   │
│  │  │  - agent_state (session_id, context, tool_history)      │   │    │   │
│  │  └──────────────────────────────────────────────────────────┘   │    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AIAgentRunner

The `AIAgentRunner` class wraps the OpenAI Agent and Runner for task orchestration.

```python
from openai import Agent, Runner, Assistant

class AIAgentRunner:
    """
    Main AI Agent orchestrator using OpenAI Agents SDK.

    Responsibilities:
    - Initialize Agent with system prompt and tools
    - Execute Runner for message processing
    - Handle tool calls via MCP Client
    - Manage conversation state via Dapr
    """

    def __init__(
        self,
        agent: Agent,
        mcp_client: MCPClient,
        dapr_state_store: DaprStateStore
    ):
        self.agent = agent
        self.mcp_client = mcp_client
        self.dapr_state_store = dapr_state_store

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
        # Load conversation from Dapr state if available
        if conversation_id:
            conversation = await self.dapr_state_store.get(
                f"conversation:{conversation_id}"
            )

        # Create Runner with conversation history
        runner = Runner(agent=self.agent, async_mode=True)

        # Execute the agent
        result = await runner.run(
            message=message,
            context={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "conversation_history": conversation.get("messages", [])
            }
        )

        # Save conversation to Dapr state
        if conversation_id:
            await self.dapr_state_store.save(
                f"conversation:{conversation_id}",
                {
                    "user_id": user_id,
                    "messages": result.context.get("conversation_history", []),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

        return {
            "response": result.output,
            "tool_results": result.tool_results or [],
            "conversation_id": conversation_id
        }
```

### 2. Agent Configuration

```python
from openai import OpenAI, Agent

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_ai_agent() -> Agent:
    """
    Create and configure the AI Agent using OpenAI Agents SDK.

    The agent uses:
    - System prompt for task management instructions
    - MCP Client for tool execution
    - Context-aware behavior
    """

    # System prompt defining agent behavior
    system_prompt = """
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

    agent = Agent(
        client=client,
        instructions=system_prompt,
        model="gpt-4o-mini",  # Cost-effective model for function calling
        tools=[],
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
```

### 3. MCP Client Integration

```python
from openai import MCPClient

class MCPClient:
    """
    MCP Client for executing tools via the MCP server.

    Uses official MCP SDK to call tools defined in MCP server.
    """

    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.client = MCPClient(server_url=server_url)

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from MCP server."""
        return await self.client.list_tools()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool via MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        result = await self.client.call_tool(
            name=tool_name,
            arguments=arguments
        )
        return result

    async def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get the schema for a specific tool."""
        tools = await self.list_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool["input_schema"]
        return None
```

### 4. Tool Handler

```python
from openai import Tool

def create_tool_handler(mcp_client: MCPClient) -> Tool:
    """
    Create a tool handler that wraps MCP tools for the Agent.

    The Agent will call this tool handler, which in turn calls the MCP server.
    """

    async def handle_tool_call(arguments: Dict[str, Any]) -> str:
        """
        Handle tool calls from the Agent.

        This function is registered as a tool with the Agent.
        It executes the actual tool via MCP server.
        """
        tool_name = arguments.pop("tool_name", None)

        if not tool_name:
            return json.dumps({
                "error": "Tool name not provided"
            })

        # Call the tool via MCP server
        result = await mcp_client.call_tool(tool_name, arguments)

        return json.dumps(result)

    return Tool(
        type="function",
        function={
            "name": "mcp_tool_handler",
            "description": "Execute a tool via MCP server",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to execute"
                    }
                },
                "required": ["tool_name"]
            }
        },
        handler=handle_tool_call
    )
```

## Agentic Loop Pattern

The Agent + Runner pattern handles the agentic loop internally:

```
User Message
       │
       ▼
┌─────────────────────────────────────────────┐
│  Runner.run(message)                        │
│                                             │
│  1. Model decides to use tools              │
│  2. Agent calls tool_handler               │
│  3. Tool_handler calls MCP server          │
│  4. MCP server executes tool function      │
│  5. Result returned to Agent               │
│  6. Model processes result                 │
│  7. If more tools needed → repeat          │
│  8. Final response generated               │
└─────────────────────────────────────────────┘
       │
       ▼
Final Response
```

## State Management

### Conversation State

```python
class ConversationState:
    """
    Manages conversation state using Dapr State Store.
    """

    def __init__(self, dapr_state_store: DaprStateStore):
        self.dapr_state_store = dapr_state_store

    async def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load conversation history from Dapr state."""
        return await self.dapr_state_store.get(
            key=f"conversation:{conversation_id}"
        )

    async def save_conversation(self, conversation_id: str, messages: List[Dict]):
        """Save conversation history to Dapr state."""
        await self.dapr_state_store.save(
            key=f"conversation:{conversation_id}",
            value={
                "messages": messages,
                "updated_at": datetime.utcnow().isoformat()
            }
        )

    async def append_message(self, conversation_id: str, role: str, content: str):
        """Append a message to conversation history."""
        conversation = await self.load_conversation(conversation_id) or {}
        messages = conversation.get("messages", [])

        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        await self.save_conversation(conversation_id, messages)
```

## Error Handling

```python
class AIAgentError(Exception):
    """Base exception for AI Agent errors."""

    pass

class ToolExecutionError(AIAgentError):
    """Raised when tool execution fails."""

    def __init__(self, tool_name: str, error: Exception):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"Tool {tool_name} execution failed: {error}")

class AgentError(AIAgentError):
    """Raised when Agent execution fails."""

    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message)
```

## Testing Strategy

### Unit Tests

```python
@pytest.mark.asyncio
async def test_agent_creates_task():
    """Test that agent can create a task using add_task tool."""
    agent = create_ai_agent()
    runner = Runner(agent=agent, async_mode=True)

    result = await runner.run(
        message="Add a task called 'Buy groceries'",
        context={"user_id": "test-user-123"}
    )

    assert "groceries" in result.output.lower()
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "add_task"

@pytest.mark.asyncio
async def test_agent_lists_tasks():
    """Test that agent can list tasks using list_tasks tool."""
    agent = create_ai_agent()
    runner = Runner(agent=agent, async_mode=True)

    result = await runner.run(
        message="Show me my tasks",
        context={"user_id": "test-user-123"}
    )

    assert "task" in result.output.lower()
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_agent_with_mcp_server():
    """Test agent can successfully call tools via MCP server."""
    mcp_client = MCPClient(server_url="http://localhost:8001")
    agent = create_ai_agent()

    # Test tool execution
    result = await mcp_client.call_tool(
        "add_task",
        {
            "title": "Test Task",
            "description": "Test description",
            "user_id": "test-user-123"
        }
    )

    assert result["status"] == "success"
    assert "test task" in result["task"]["title"].lower()
```

## Performance Considerations

1. **Concurrency**: Agent + Runner supports async execution
2. **Caching**: Use Dapr State Store to cache conversation history
3. **Timeouts**: Set appropriate timeouts for tool calls
4. **Rate Limiting**: Handle API rate limits gracefully

## Security

1. **User Isolation**: All tool calls scoped to user_id
2. **Input Validation**: Validate all tool arguments
3. **Secrets Management**: Use Dapr Secrets for API keys
4. **Authentication**: Validate user session before allowing chat

## Migration from Current Implementation

### Current Issues

1. Not using OpenAI Agents SDK
2. Not using official MCP SDK
3. Direct function calls instead of MCP client
4. No proper state management

### Migration Steps

1. Replace `chat.completions.create()` with `Agent + Runner`
2. Replace direct tool imports with `MCPClient`
3. Add Dapr State Store for conversation persistence
4. Implement proper error handling

## References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [OpenAI Runner Pattern](https://platform.openai.com/docs/agents/runners)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
