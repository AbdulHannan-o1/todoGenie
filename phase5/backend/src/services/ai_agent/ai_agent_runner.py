"""
AI Agent orchestrator for processing user messages.

Uses OpenAI chat.completions API with MCP Client for tool execution.
This follows the standard function calling pattern.
"""
import os
from typing import Dict, Any, Optional, List

from openai import OpenAI
from .mcp_client import MCPClient


class AIAgentError(Exception):
    """Base exception for AI Agent errors."""

    pass


class ToolExecutionError(AIAgentError):
    """Raised when tool execution fails."""

    def __init__(self, tool_name: str, error: Exception):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"Tool {tool_name} execution failed: {error}")


class AIAgentRunner:
    """
    AI Agent orchestrator using OpenAI chat.completions API with MCP Client.

    Uses standard function calling pattern with tool execution via MCP.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the AI Agent Runner.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        self.mcp_client = MCPClient()
        self.client = OpenAI(api_key=self.openai_api_key)
        self.tools = self._get_tools()

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the tool definitions for the AI agent.

        Returns:
            List of tool definitions compatible with OpenAI API
        """
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
            Dict with 'response', 'tool_results', and 'conversation_id'

        Raises:
            AIAgentError: If agent execution fails
        """
        try:
            # Initialize MCP client
            await self.mcp_client.connect()

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": message}
            ]

            # Agentic loop: keep calling the AI until it stops making tool calls
            max_iterations = 50
            all_tool_results = []

            for iteration in range(max_iterations):
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    max_tokens=500,
                    temperature=0.7,
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # If no tool calls, we're done with the loop
                if not tool_calls:
                    break

                # Add assistant's message to conversation
                messages.append(response_message)

                # Execute all tool calls in this iteration
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = {}

                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except:
                        function_args = {}

                    # Execute the tool via MCP client
                    result = await self.mcp_client.call_tool(function_name, function_args)

                    # Get tool results
                    tool_results = []
                    if isinstance(result, dict) and "content" in result:
                        # Handle MCP response format
                        tool_results.append({
                            "tool": function_name,
                            "result": result["content"]
                        })
                    else:
                        # Handle direct dict result
                        tool_results.append({
                            "tool": function_name,
                            "result": result
                        })

                    all_tool_results.extend(tool_results)

                    # Add tool response to messages for next iteration
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    })

            await self.mcp_client.close()

            # Get final response text
            final_response_text = response_message.content if response_message else None

            return {
                "response": final_response_text or "✅ Task completed successfully.",
                "tool_results": all_tool_results,
                "conversation_id": conversation_id
            }

        except Exception as e:
            await self.mcp_client.close()
            if isinstance(e, AIAgentError):
                raise
            raise AIAgentError(f"Agent execution failed: {e}")

    async def close(self) -> None:
        """Close the MCP client connection."""
        await self.mcp_client.close()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
