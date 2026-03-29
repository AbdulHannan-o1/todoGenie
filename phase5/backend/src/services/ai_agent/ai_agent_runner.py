"""
AI Agent orchestrator for processing user messages.

Uses OpenAI Agents SDK with MCP Client for tool execution.
Agent calls MCP server via HTTP instead of direct function calls.
This follows the Phase V hackathon requirements.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from agents import Agent, Runner, function_tool, AsyncOpenAI, set_default_openai_client, set_default_openai_api
from .mcp_client import MCPClient


# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


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
    AI Agent orchestrator using OpenAI Agents SDK with MCP Client.

    Agent calls MCP server via HTTP instead of direct function calls.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        mcp_client: Optional[MCPClient] = None
    ):
        """
        Initialize the AI Agent Runner.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            model: Model to use (chat_completion, response, or assistant)
            mcp_client: Optional MCP client instance
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        self.model = model
        self.mcp_client = mcp_client or MCPClient()

        # Set default OpenAI API type to chat_completions
        set_default_openai_api("chat_completions")

        # Create OpenAI-compatible client
        self.openai_client = AsyncOpenAI(
            api_key=self.openai_api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        set_default_openai_client(self.openai_client)

        # Create Agent with MCP tool function
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create Agent using MCP tool function.

        Returns:
            Configured Agent instance
        """
        agent = Agent(
            name="TaskManager",
            instructions=self._get_system_prompt(),
            model=self.model,
            tools=[self._mcp_tool_function],
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

        AVAILABLE TOOLS (via MCP Server):
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

    @function_tool
    async def _mcp_tool_function(self, tool_name: str, arguments) -> dict:
        """
        MCP tool function that Agent calls to execute tools via MCP Server.

        This function is registered with the Agent, but it calls the MCP server
        via HTTP instead of executing directly.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dictionary

        Returns:
            Tool execution result
        """
        try:
            result = await self.mcp_client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "type": type(e).__name__
            }

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
