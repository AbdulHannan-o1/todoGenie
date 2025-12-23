"""
AI Agent service for processing natural language commands using OpenAI-compatible API
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
        # Initialize OpenAI client with Google Gemini configuration
        # Get API key from environment (try multiple possible variable names)
        api_key = settings.google_gemini_api_key or settings.openai_api_key
        if not api_key:
            # Try to get from environment directly in case the config isn't reading it properly
            import os
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Use the Google OpenAI-compatible endpoint from settings
        base_url = settings.openai_api_base

        self.client = OpenAI(
            api_key=api_key,  # For Google's API, this should be the API key
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
                                "title": {"type": "string", "description": "The task title"},
                                "description": {"type": "string", "description": "The task description"},
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
                    "You are a helpful AI assistant that helps users manage their tasks. "
                    "You can create, list, update, delete, and mark tasks as complete. "
                    "Always try to understand the user's intent and call the appropriate function. "
                    "If you're not sure about specific task IDs, ask the user to clarify. "
                    "Validate task IDs before performing operations and handle errors gracefully. "
                    "If a task ID is invalid or not found, inform the user and suggest listing tasks first. "
                    "For voice input, the user may speak in a more conversational tone, so interpret accordingly. "
                    "When a user says something like 'remind me to buy groceries' or 'add a task to call mom', "
                    "understand that they want to create a task. "
                    "When they say 'show my tasks' or 'what do I have to do', they want to list tasks. "
                    "When they say 'mark task 3 as done' or 'complete the meeting task', they want to complete a task. "
                    "Always provide helpful and clear feedback to the user about the results of their requests."
                )
            }

            # Prepare the user message
            user_message = {
                "role": "user",
                "content": message
            }

            # Call the OpenAI API with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[system_message, user_message],
                tools=tools,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7,
            )

            # Process the response
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Execute the tool calls
                results = []
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

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
                            result = complete_task_tool(**function_args)
                        else:
                            result = {"status": "error", "message": f"Unknown function: {function_name}"}
                    except Exception as tool_error:
                        result = {
                            "status": "error",
                            "message": f"Error executing {function_name}: {str(tool_error)}"
                        }

                    # Log tool execution
                    ai_logger.log_tool_execution(
                        user_id=user_id,
                        conversation_id=conversation_id or "unknown",
                        tool_name=function_name,
                        tool_params=function_args,
                        success=result.get("status") != "error",
                        execution_time=0.0  # We could add more precise timing if needed
                    )

                    results.append({
                        "tool_call_id": tool_call.id,
                        "result": result
                    })

                # Get a final response from the AI based on the tool results
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        system_message,
                        user_message,
                        response_message,
                        {
                            "role": "tool",
                            "content": json.dumps([r["result"] for r in results]),
                            "tool_call_id": results[0]["tool_call_id"] if results else ""
                        }
                    ],
                    max_tokens=300,
                    temperature=0.7,
                )

                processing_time = time.time() - start_time

                # Log the AI response
                ai_logger.log_ai_response(
                    user_id=user_id,
                    conversation_id=conversation_id or "unknown",
                    request_content=message,
                    response_content=final_response.choices[0].message.content,
                    processing_time=processing_time,
                    success=True,
                    tool_results=results
                )

                return {
                    "response": final_response.choices[0].message.content,
                    "tool_results": [r["result"] for r in results],
                    "success": True
                }
            else:
                # If no tool calls were made, return the AI's direct response
                processing_time = time.time() - start_time

                # Log the AI response (without tools)
                ai_logger.log_ai_response(
                    user_id=user_id,
                    conversation_id=conversation_id or "unknown",
                    request_content=message,
                    response_content=response_message.content,
                    processing_time=processing_time,
                    success=True,
                    tool_results=[]
                )

                return {
                    "response": response_message.content,
                    "tool_results": [],
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