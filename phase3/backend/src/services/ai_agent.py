"""
AI Agent service for processing natural language commands using z.ai GLM OpenAI-compatible API
"""
import asyncio
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from src.core.config import settings
from src.models.conversation import MessageCreate
from src.services.mcp_server.todo_tools import (
    create_task_tool, list_tasks_tool, update_task_tool,
    delete_task_tool, complete_task_tool
)
from src.core.logging import ai_logger, performance_monitor
import json


class AIAgentService:
    def __init__(self):
        # Initialize OpenAI client with appropriate API key based on base URL
        import os
        base_url = settings.openai_api_base

        # Select the right API key based on the base URL
        if "groq.com" in base_url:
            api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        elif "trybons.ai" in base_url:
            api_key = settings.bonsai_api_key or os.getenv("BONSAI_API_KEY")
        elif "openrouter.ai" in base_url:
            api_key = settings.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        elif "bigmodel.cn" in base_url:
            api_key = settings.zai_api_key or os.getenv("ZAI_API_KEY")
        else:
            # Fallback: try all keys in order
            api_key = settings.openai_api_key or settings.groq_api_key or settings.bonsai_api_key or settings.openrouter_api_key
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("BONSAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = settings.ai_model

    async def process_message(self,
                            message: str,
                            user_id: str,
                            conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message and return the AI response
        """
        start_time = time.time()

        # Log the incoming AI request
        ai_logger.log_ai_request(
            user_id=user_id,
            conversation_id=conversation_id or "unknown",
            message_content=message,
            message_type="text"  # Default to text, voice would be handled elsewhere
        )

        try:
            # Define the tools available to the AI agent
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "create_task",
                        "description": "Create a new task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title"},
                                "description": {"type": "string", "description": "Task description"},
                                "tags": {"type": "string", "description": "Tags (comma-separated)"},
                                "priority": {"type": "string", "description": "Priority: low, medium, high"},
                                "due_date": {"type": "string", "description": "Due date (ISO format)"},
                            },
                            "required": ["title"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List all tasks for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Update an existing task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string", "description": "The ID of the task to update"},
                                "title": {"type": "string", "description": "The new title"},
                                "description": {"type": "string", "description": "The new description"},
                                "status": {"type": "string", "description": "The new status"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Delete a task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string", "description": "The ID of the task to delete"},
                            },
                            "required": ["task_id"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string", "description": "The ID of the task to complete"},
                                "completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"},
                            },
                            "required": ["task_id"],
                        },
                    },
                }
            ]

            # Prepare the system message to guide the AI's behavior
            system_message = {
                "role": "system",
                "content": (
                    "You are a task management AI assistant. You can create, list, update, delete, and complete tasks.\n\n"
                    "IMPORTANT: When creating tasks, map user input to the correct fields:\n"
                    "- title: Main task name\n"
                    "- description: Details about the task\n"
                    "- tags: Categories (comma-separated)\n"
                    "- priority: low, medium, or high\n"
                    "- due_date: Date in ISO format\n\n"
                    "NEVER put tags, priority, or dates in description. Use the specific fields.\n\n"
                    "For operations on existing tasks (complete, update, delete), call list_tasks() first to get the task ID, "
                    "then use that ID in the next function call."
                )
            }

            # Prepare the user message
            user_message = {
                "role": "user",
                "content": message
            }

            # Agentic loop: keep calling the AI until it stops making tool calls
            messages = [system_message, user_message]
            max_iterations = 5  # Prevent infinite loops
            all_tool_results = []

            for iteration in range(max_iterations):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=500,
                        temperature=0.7,
                    )
                except Exception as api_error:
                    # Check if this is a tool_use_failed error
                    error_str = str(api_error)
                    if "tool_use_failed" in error_str or "Failed to call a function" in error_str:
                        # Model had trouble with function calling format - retry without tools
                        simple_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7,
                        )
                        final_response_text = simple_response.choices[0].message.content
                        processing_time = time.time() - start_time

                        ai_logger.log_ai_response(
                            user_id=user_id,
                            conversation_id=conversation_id or "unknown",
                            request_content=message,
                            response_content=final_response_text,
                            processing_time=processing_time,
                            success=True,
                            tool_results=[]
                        )

                        return {
                            "response": final_response_text,
                            "tool_results": [],
                            "success": True
                        }
                    else:
                        # Re-raise other errors
                        raise api_error

                # Process the response
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
                    function_args = json.loads(tool_call.function.arguments)

                    # Handle null arguments (for functions that don't require args like list_tasks)
                    if function_args is None:
                        function_args = {}

                    # Add user_id to the function arguments where needed
                    function_args["user_id"] = user_id

                    # Execute the appropriate tool function with enhanced error handling
                    try:
                        if function_name == "create_task":
                            result = create_task_tool(**function_args)
                        elif function_name == "list_tasks":
                            result = list_tasks_tool(user_id=function_args["user_id"])
                        elif function_name == "update_task":
                            result = update_task_tool(**function_args)
                        elif function_name == "delete_task":
                            result = delete_task_tool(**function_args)
                        elif function_name == "complete_task":
                            # complete_task doesn't need user_id, so we exclude it
                            task_args = {k: v for k, v in function_args.items() if k != "user_id"}
                            result = complete_task_tool(**task_args)
                        else:
                            result = {"status": "error", "message": f"Unknown function: {function_name}"}
                    except Exception as tool_error:
                        result = {
                            "status": "error",
                            "message": f"Error executing {function_name}: {str(tool_error)}"
                        }

                    # Log tool execution
                    # Determine success based on whether result is a dict with status != "error"
                    # or if it's a list (like from list_tasks), assume success
                    is_success = True
                    if isinstance(result, dict):
                        is_success = result.get("status") != "error"
                    # For lists (like from list_tasks), we consider it successful if no exception occurred

                    ai_logger.log_tool_execution(
                        user_id=user_id,
                        conversation_id=conversation_id or "unknown",
                        tool_name=function_name,
                        tool_params=function_args,
                        success=is_success,
                        execution_time=0.0
                    )

                    all_tool_results.append({"tool": function_name, "result": result})

                    # Add tool response to messages for next iteration
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    })

            # After loop completes, get final response text
            final_response_text = response_message.content if response_message and response_message.content else "Task completed successfully."

            processing_time = time.time() - start_time

            # Log the AI response
            ai_logger.log_ai_response(
                user_id=user_id,
                conversation_id=conversation_id or "unknown",
                request_content=message,
                response_content=final_response_text,
                processing_time=processing_time,
                success=True,
                tool_results=all_tool_results
            )

            return {
                "response": final_response_text,
                "tool_results": [r["result"] for r in all_tool_results],
                "success": True
            }

        except Exception as e:
            processing_time = time.time() - start_time

            # Log the error for debugging
            ai_logger.log_ai_error(
                user_id=user_id,
                conversation_id=conversation_id or "unknown",
                error_message=str(e),
                error_type=type(e).__name__,
                request_content=message
            )

            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Agent error processing message: {str(e)}", exc_info=True)

            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "tool_results": [],
                "success": False,
                "error": str(e)
            }

    async def chat_with_context(self,
                              message: str,
                              user_id: str,
                              conversation_history: list = None) -> Dict[str, Any]:
        """
        Process a message with conversation context
        """
        start_time = time.time()

        # Log the incoming AI request
        ai_logger.log_ai_request(
            user_id=user_id,
            conversation_id="context-chat",
            message_content=message,
            message_type="text"
        )

        try:
            # In a real implementation, we would use the conversation history
            # For now, we'll just call the basic process_message function
            result = await self.process_message(message, user_id)

            # Log the AI response
            ai_logger.log_ai_response(
                user_id=user_id,
                conversation_id="context-chat",
                request_content=message,
                response_content=result.get("response", ""),
                processing_time=time.time() - start_time,
                success=result.get("success", False),
                tool_results=result.get("tool_results", [])
            )

            return result
        except Exception as e:
            processing_time = time.time() - start_time

            # Log the error for debugging
            ai_logger.log_ai_error(
                user_id=user_id,
                conversation_id="context-chat",
                error_message=str(e),
                error_type=type(e).__name__,
                request_content=message
            )

            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Agent error processing message: {str(e)}", exc_info=True)

            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "tool_results": [],
                "success": False,
                "error": str(e)
            }


# Global AI agent instance
ai_agent_service = AIAgentService()