# Chat API Endpoint Specification

## Overview

This document defines the Chat API endpoint implementation for the Todo AI Chatbot, following the stateless chat pattern as required by the hackathon specification.

## API Endpoint

```
POST /api/{user_id}/chat
```

### Request

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | Yes | User identifier (URL parameter) |
| `message` | string | Yes | User's message to send to the AI agent |
| `conversation_id` | string | No | Optional conversation ID for stateful chat |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Content-Type` | string | Yes | `application/json` |
| `Authorization` | string | Yes | Bearer token from authentication |

### Example Request

```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Add a task called Buy groceries",
    "conversation_id": "conv-abc-123"
  }'
```

### Response

| Property | Type | Description |
|----------|------|-------------|
| `response` | string | AI agent's response text |
| `tool_results` | array | List of tool execution results |
| `conversation_id` | string | Generated or provided conversation ID |
| `success` | boolean | Whether the request was successful |
| `error` | string | Error message (if any) |

### Success Response (200 OK)

```json
{
  "response": "✅ I've added your task 'Buy groceries' with priority high.",
  "tool_results": [
    {
      "tool": "add_task",
      "result": {
        "status": "success",
        "task": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "title": "Buy groceries",
          "description": null,
          "status": "pending",
          "priority": "high",
          "user_id": "user123"
        },
        "message": "Task created successfully"
      }
    }
  ],
  "conversation_id": "conv-abc-123",
  "success": true
}
```

### Error Responses

**401 Unauthorized**
```json
{
  "error": "Invalid or expired token",
  "success": false
}
```

**404 Not Found**
```json
{
  "error": "User not found",
  "success": false
}
```

**500 Internal Server Error**
```json
{
  "error": "Failed to process message",
  "success": false
}
```

## Implementation

### FastAPI Route

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from src.services.ai_agent.ai_agent_runner import AIAgentRunner
from src.services.ai_agent.mcp_client import MCPClient
from src.core.auth import get_current_user
from src.models.user import User

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
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process a user message through the AI agent.

    This endpoint is stateless - it accepts a conversation_id if provided,
    but the actual conversation state is managed separately (e.g., via Dapr).
    """
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4()}"

    try:
        # Initialize AI Agent Runner
        agent_runner = AIAgentRunner(
            mcp_client=MCPClient(),
            dapr_state_store=DaprStateStore()
        )

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
        # Log error
        logger.error(f"Chat error for user {user_id}: {e}", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )
```

### AIAgentRunner Integration

```python
from openai import Agent, Runner

class AIAgentRunner:
    """
    AI Agent orchestrator using OpenAI Agents SDK.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
        dapr_state_store: DaprStateStore
    ):
        self.mcp_client = mcp_client
        self.dapr_state_store = dapr_state_store

        # Create the Agent
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create and configure the AI Agent."""
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        """Get the system prompt for the agent."""
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
        # Load conversation from Dapr state if available
        conversation = None
        if conversation_id:
            conversation = await self.dapr_state_store.get(
                key=f"conversation:{conversation_id}"
            )

        # Create Runner with conversation history
        runner = Runner(agent=self.agent, async_mode=True)

        # Execute the agent
        result = await runner.run(
            message=message,
            context={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "conversation_history": conversation.get("messages", []) if conversation else []
            }
        )

        # Save conversation to Dapr state
        if conversation_id:
            await self.dapr_state_store.save(
                key=f"conversation:{conversation_id}",
                value={
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

### Dapr State Store Integration

```python
from dapr.clients import DaprClient

class DaprStateStore:
    """
    Dapr state store for managing conversation state.

    Uses Dapr State Store with PostgreSQL backend.
    """

    def __init__(self, store_name: str = "statestore"):
        self.store_name = store_name
        self.dapr_client = DaprClient()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from Dapr state store."""
        try:
            response = self.dapr_client.get_state(
                store_name=self.store_name,
                key=key
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return None

    async def save(self, key: str, value: Dict[str, Any]) -> None:
        """Save a value to Dapr state store."""
        try:
            self.dapr_client.save_state(
                store_name=self.store_name,
                key=key,
                value=json.dumps(value),
                metadata={"contentType": "application/json"}
            )
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            raise

    async def delete(self, key: str) -> None:
        """Delete a value from Dapr state store."""
        try:
            self.dapr_client.delete_state(
                store_name=self.store_name,
                key=key
            )
        except Exception as e:
            logger.error(f"Error deleting state: {e}")
```

## Stateless Chat Pattern

The endpoint is designed to be stateless:

1. **User provides conversation_id** - If provided, the conversation is loaded from Dapr state
2. **Agent processes message** - Using the Agent + Runner pattern
3. **Conversation is saved** - The updated conversation is saved back to Dapr state
4. **No session in memory** - The backend does not maintain session state in memory

This pattern ensures:
- Horizontal scalability
- No session affinity requirements
- Resilience to pod restarts
- Easy load balancing

## Conversation Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Conversation Lifecycle                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User sends POST /api/{user_id}/chat with conversation_id    │
│     ↓                                                           │
│  2. Endpoint loads conversation from Dapr state                │
│     ↓                                                           │
│  3. Agent Runner processes message with conversation history   │
│     ↓                                                           │
│  4. Agent may call tools (MCP Client → MCP Server)             │
│     ↓                                                           │
│  5. Result saved back to Dapr state                            │
│     ↓                                                           │
│  6. Response returned to user                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling

```python
from fastapi import HTTPException, status

async def chat_endpoint(user_id: str, request: ChatRequest):
    try:
        # ... processing ...

    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except PermissionError:
        # User not authenticated
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    except Exception as e:
        # Server errors
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )
```

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/{user_id}/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # 10 messages per minute per user
async def chat_endpoint(...):
    # ...
```

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_chat_endpoint_creates_task():
    """Test that chat endpoint can create a task."""
    client = TestClient(app)

    response = client.post(
        "/api/user123/chat",
        json={
            "message": "Add a task called Buy groceries",
            "conversation_id": "test-conv"
        },
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "groceries" in data["response"].lower()
    assert len(data["tool_results"]) == 1
    assert data["tool_results"][0]["tool"] == "add_task"

@pytest.mark.asyncio
async def test_chat_endpoint_stateless():
    """Test that the endpoint is stateless."""
    client = TestClient(app)

    # First message
    response1 = client.post(
        "/api/user123/chat",
        json={"message": "Add task A"},
        headers={"Authorization": "Bearer test-token"}
    )
    conv_id = response1.json()["conversation_id"]

    # Second message with same conversation_id
    response2 = client.post(
        "/api/user123/chat",
        json={
            "message": "Add task B",
            "conversation_id": conv_id
        },
        headers={"Authorization": "Bearer test-token"}
    )

    # Both should succeed
    assert response1.status_code == 200
    assert response2.status_code == 200
```

### Integration Tests

```python
@pytest.mark.integration
async def test_chat_with_real_agent():
    """Test chat endpoint with real AI agent (requires OpenAI API key)."""
    client = TestClient(app)

    response = client.post(
        "/api/test-user/chat",
        json={"message": "Show me my tasks"},
        headers={"Authorization": f"Bearer {os.getenv('TEST_TOKEN')}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "task" in data["response"].lower()
```

## Performance Considerations

1. **Async execution** - All operations are asynchronous
2. **Dapr state store** - No in-memory session state
3. **Connection pooling** - Dapr client uses connection pooling
4. **Caching** - Consider caching conversation history

## Security

1. **Authentication** - Requires valid Bearer token
2. **User isolation** - All operations scoped to user_id
3. **Input validation** - Validate all input parameters
4. **Rate limiting** - Prevent abuse

## References

- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- [Stateless API Design](https://restfulapi.net/stateless/)
