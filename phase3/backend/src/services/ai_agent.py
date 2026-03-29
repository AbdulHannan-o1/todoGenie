"""
AI Agent service for processing natural language commands with primary (Groq) and backup (Bonsai) providers

This implementation follows the hackathon spec:
- LLM interprets ALL user intent (no hardcoded keyword detection)
- Conversation history is fetched from DB and passed to LLM
- MCP tools are called autonomously by the LLM
"""
import time
from typing import Dict, Any, Optional, List
from uuid import UUID
from openai import OpenAI
from src.core.config import settings
from src.services.mcp_server.todo_tools import (
    create_task_tool, list_tasks_tool, update_task_tool,
    delete_task_tool, complete_task_tool, get_task_details_tool
)
from src.core.logging import ai_logger
import json


class AIAgentService:
    # Primary (Groq) and backup (Bonsai) provider configurations
    PROVIDERS = {
        "primary": {
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.3-70b-versatile",
            "api_key_attr": "groq_api_key",
            "api_key_env": "GROQ_API_KEY"
        },
        "backup": {
            "base_url": "https://go.trybons.ai",
            "model": "claude-sonnet-4-20250514",
            "api_key_attr": "bonsai_api_key",
            "api_key_env": "BONSAI_API_KEY"
        }
    }

    def __init__(self):
        import os
        # Initialize with primary provider (Groq)
        self.primary_client = self._create_client("primary")
        self.backup_client = self._create_client("backup")
        self.current_client = self.primary_client
        self.current_model = self.PROVIDERS["primary"]["model"]
        self.current_provider = "primary"
        self.max_history_messages = 10  # Number of previous messages to include for context

    def _create_client(self, provider_type: str) -> OpenAI:
        """Create an OpenAI client for the specified provider"""
        config = self.PROVIDERS[provider_type]
        base_url = config["base_url"]

        # Get API key from settings or environment
        api_key_attr = config["api_key_attr"]
        api_key = getattr(settings, api_key_attr, None)

        if not api_key:
            import os
            api_key = os.getenv(config["api_key_env"])

        return OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def switch_to_backup(self):
        """Switch to backup provider (Bonsai)"""
        self.current_client = self.backup_client
        self.current_model = self.PROVIDERS["backup"]["model"]
        self.current_provider = "backup"

    def switch_to_primary(self):
        """Switch back to primary provider (Groq)"""
        self.current_client = self.primary_client
        self.current_model = self.PROVIDERS["primary"]["model"]
        self.current_provider = "primary"

    async def _get_conversation_history(
        self,
        conversation_id: Optional[str],
        user_id: str,
        max_messages: int = None
    ) -> List[Dict[str, str]]:
        """
        Fetch last N messages from conversation history.
        Returns list of {role, content} dicts for LLM.
        
        This enables the LLM to understand context from previous messages,
        allowing it to resolve pronouns ("it", "that task") and follow-up questions.
        """
        if not conversation_id:
            return []
        
        if max_messages is None:
            max_messages = self.max_history_messages
        
        try:
            from src.db import get_session
            from src.models.conversation import Message
            from sqlmodel import select
            
            with next(get_session()) as session:
                statement = (
                    select(Message)
                    .where(Message.conversation_id == UUID(conversation_id))
                    .order_by(Message.timestamp.desc())
                    .limit(max_messages)
                )
                messages = session.exec(statement).all()
                
                # Reverse to get chronological order (oldest first)
                return [
                    {"role": msg.role, "content": msg.content}
                    for msg in reversed(messages)
                ]
        except Exception as e:
            ai_logger.logger.warning(f"Failed to fetch conversation history: {e}")
            return []  # Return empty list on error, don't break the flow

    async def process_message(self,
                            message: str,
                            user_id: str,
                            conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message and return the AI response.
        
        FLOW (per hackathon spec):
        1. Fetch conversation history from DB
        2. Send history + current message to LLM
        3. LLM interprets intent and decides which tool to call
        4. Execute tools called by LLM
        5. Return LLM's natural language response
        
        NO hardcoded keyword detection - LLM handles ALL intent interpretation.
        """
        start_time = time.time()

        # Log the incoming AI request
        ai_logger.log_ai_request(
            user_id=user_id,
            conversation_id=conversation_id or "unknown",
            message_content=message,
            message_type="text"
        )

        try:
            # STEP 1: Fetch conversation history for context
            conversation_history = await self._get_conversation_history(
                conversation_id=conversation_id,
                user_id=user_id,
                max_messages=self.max_history_messages
            )
            
            # STEP 2: Define the tools available to the AI agent
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "create_task",
                        "description": "Create a new task. Use when user wants to add/create/schedule a new todo item.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title (required)"},
                                "description": {"type": "string", "description": "Task description (optional)"},
                                "tags": {"type": "string", "description": "Tags, comma-separated (optional)"},
                                "priority": {"type": "string", "description": "Priority: low, medium, high", "enum": ["low", "medium", "high"]},
                                "due_date": {"type": "string", "description": "Due date in ISO format (optional)"},
                            },
                            "required": ["title"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List tasks for the user. Can filter by status (pending/completed/all), priority, tags, or search keywords. Use when user asks to see/show/list tasks.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "description": "Filter by status: 'pending', 'completed', or 'all'. Default: 'all'",
                                    "enum": ["pending", "completed", "all"]
                                },
                                "priority": {
                                    "type": "string",
                                    "description": "Filter by priority: 'high', 'medium', 'low'",
                                    "enum": ["high", "medium", "low"]
                                },
                                "tags": {
                                    "type": "string",
                                    "description": "Filter by tags (comma-separated)"
                                },
                                "search": {
                                    "type": "string",
                                    "description": "Search keywords in title and description"
                                }
                            }
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_task_details",
                        "description": "Get detailed information about a specific task by ID. Use when user asks about a specific task's details, description, or status.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "The UUID of the task to get details for"
                                }
                            },
                            "required": ["task_id"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Update an existing task's title, description, status, priority, or due date. Use when user wants to modify/change/edit a task.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string", "description": "The ID of the task to update"},
                                "title": {"type": "string", "description": "The new title"},
                                "description": {"type": "string", "description": "The new description"},
                                "status": {"type": "string", "description": "The new status"},
                                "priority": {"type": "string", "description": "The new priority"},
                                "due_date": {"type": "string", "description": "The new due date"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Delete a task permanently. Use when user wants to remove/delete/erase a task.",
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
                        "description": "Mark a task as complete or incomplete. Use when user wants to mark/finish/done with a task.",
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
                    "You are a friendly AI companion and task manager. Your personality is empathetic, supportive, and helpful like a close friend.\n\n"

                    "CORE IDENTITY:\n"
                    "- Be warm, conversational, and genuinely caring\n"
                    "- Listen actively and offer helpful suggestions\n"
                    "- Seamlessly blend friendship with task management\n\n"

                    "TASK MANAGEMENT CAPABILITIES:\n"
                    "You can create, list, get details, update, delete, and complete tasks using these tools:\n"
                    "- create_task: Create new tasks\n"
                    "- list_tasks: Show current tasks (supports filters: status, priority, tags, search)\n"
                    "- get_task_details: Get detailed info about a specific task\n"
                    "- update_task: Modify existing tasks\n"
                    "- delete_task: Remove tasks\n"
                    "- complete_task: Mark tasks as done\n\n"

                    "CONTEXT AWARENESS:\n"
                    "- You have access to the last 10 messages in this conversation\n"
                    "- Reference previous messages when user says 'that task', 'the one I mentioned', etc.\n"
                    "- If user refers to something from earlier, use conversation history to understand\n"
                    "- Resolve pronouns like 'it', 'them', 'that one' from context\n\n"

                    "TASK QUERY INTELLIGENCE:\n"
                    "- When user asks 'what are my completed tasks?' → call list_tasks(status='completed')\n"
                    "- When user asks 'show pending tasks' → call list_tasks(status='pending')\n"
                    "- When user asks 'tell me about [task name]' → first call list_tasks(search='[task name]'), then get_task_details(task_id)\n"
                    "- When user asks 'high priority stuff' → call list_tasks(priority='high')\n"
                    "- When user asks 'tasks about [topic]' → call list_tasks(search='[topic]')\n"
                    "- When user asks 'what are my tasks' → call list_tasks(status='pending') to show pending tasks\n\n"

                    "TASK ID RESOLUTION:\n"
                    "- If user says 'task 3' or 'the third task', first call list_tasks() to get the list\n"
                    "- Count to find the task at position 3, extract its ID, then operate on it\n"
                    "- Never assume task IDs are sequential numbers\n\n"

                    "TASK CREATION GUIDELINES:\n"
                    "- title: Main task (extract from conversation)\n"
                    "- description: Details (derive from context)\n"
                    "- priority: low, medium, or high (infer from urgency words like 'urgent', 'important', 'ASAP')\n"
                    "- due_date: ISO format (convert from natural language like 'tomorrow', 'next week')\n"
                    "- tags: Categories (derive from context like 'work', 'personal', 'health')\n\n"

                    "RESPONSE FORMAT:\n"
                    "- Be conversational and friendly\n"
                    "- When showing tasks, format clearly with status indicators:\n"
                    "  * Completed tasks: ✅ Task Name\n"
                    "  * Pending tasks: ⏳ Task Name\n"
                    "- Always mention due dates if they exist\n"
                    "- Keep responses concise but informative\n\n"

                    "GUARDRAILS:\n"
                    "- Maintain professional yet friendly boundaries\n"
                    "- Never share confidential information\n"
                    "- Keep conversations respectful and appropriate\n"
                    "- Focus on productivity and wellbeing\n"
                    "- Offer helpful suggestions proactively\n"
                    "- Be supportive during stressful times\n\n"

                    "PERSONALITY TRAITS:\n"
                    "- Empathetic listener\n"
                    "- Proactive helper\n"
                    "- Encouraging friend\n"
                    "- Efficient organizer\n\n"

                    "When user shares concerns (like being late), acknowledge their feelings first, then suggest helpful actions like task management to prevent future issues."
                )
            }

            # STEP 3: Prepare the user message
            user_message = {
                "role": "user",
                "content": message
            }

            # STEP 4: Build messages array with conversation history
            # Format: [system, ...history, current_user_message]
            messages = [system_message] + conversation_history + [user_message]
            
            # STEP 5: Agentic loop - keep calling the AI until it stops making tool calls
            max_iterations = 5  # Prevent infinite loops
            all_tool_results = []

            for iteration in range(max_iterations):
                try:
                    response = self.current_client.chat.completions.create(
                        model=self.current_model,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=500,
                        temperature=0.7,
                    )
                except Exception as api_error:
                    error_str = str(api_error)

                    # Try failover to backup provider if primary failed and we haven't tried backup yet
                    if self.current_provider == "primary" and ("rate limit" in error_str.lower() or "api" in error_str.lower() or "connection" in error_str.lower() or "timeout" in error_str.lower() or "access has been paused" in error_str.lower()):
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Primary provider (Groq) failed: {error_str}. Switching to backup (Bonsai).")

                        # Switch to backup and retry
                        self.switch_to_backup()

                        # Re-try with backup provider
                        try:
                            response = self.current_client.chat.completions.create(
                                model=self.current_model,
                                messages=messages,
                                tools=tools,
                                tool_choice="auto",
                                max_tokens=500,
                                temperature=0.7,
                            )
                        except Exception as backup_error:
                            # If backup also fails, raise the error
                            raise backup_error

                    # Check if this is a tool_use_failed error
                    elif "tool_use_failed" in error_str or "Failed to call a function" in error_str:
                        # Model had trouble with function calling format - retry without tools
                        simple_response = self.current_client.chat.completions.create(
                            model=self.current_model,
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
                            result = list_tasks_tool(**function_args)
                        elif function_name == "get_task_details":
                            result = get_task_details_tool(**function_args)
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
            final_response_text = response_message.content if response_message and response_message.content else None

            # Check if any tool was called and use their results for meaningful responses
            if all_tool_results:
                # Look for specific tool results to format response
                list_tasks_result = None
                operation_message = None

                for tool_result in all_tool_results:
                    result = tool_result.get("result")
                    tool_name = tool_result.get("tool")

                    if tool_name == "list_tasks" and isinstance(result, list):
                        list_tasks_result = result
                    elif isinstance(result, dict):
                        msg = result.get("message", "")
                        status = result.get("status", "")

                        # Get meaningful message for operations
                        if status == "success" and msg:
                            if tool_name == "create_task":
                                operation_message = f"✅ {msg}"
                            elif tool_name == "update_task":
                                operation_message = f"✏️ {msg}"
                            elif tool_name == "delete_task":
                                operation_message = f"🗑️ {msg}"
                            elif tool_name == "complete_task":
                                operation_message = f"✅ {msg}"
                            elif tool_name == "get_task_details":
                                # Format task details nicely
                                if "task" in result:
                                    task = result["task"]
                                    operation_message = f"📋 **{task.get('title', 'Task')}**\n"
                                    if task.get('description'):
                                        operation_message += f"\n{task['description']}\n"
                                    if task.get('priority'):
                                        operation_message += f"\nPriority: {task['priority'].capitalize()}\n"
                                    if task.get('due_date'):
                                        due = task['due_date'].split('T')[0]
                                        operation_message += f"Due: {due}\n"
                                    if task.get('status'):
                                        operation_message += f"Status: {task['status']}\n"

                # Priority: list_tasks > operation_message > AI response > default
                if list_tasks_result is not None and len(list_tasks_result) > 0:
                    # Format as priority groups
                    high_priority = []
                    medium_priority = []
                    low_priority = []
                    no_priority = []

                    for task in list_tasks_result:
                        if isinstance(task, dict):
                            title = task.get("title", "Untitled")
                            due_date = task.get("due_date")
                            if due_date and isinstance(due_date, str) and "T" in due_date:
                                due_date = due_date.split("T")[0]
                            priority = task.get("priority", "").lower() if task.get("priority") else ""
                            status = task.get("status", "pending")
                            
                            # Status indicator
                            status_icon = "✅" if status == "completed" else "⏳"
                            task_info = f"{status_icon} {title}"
                            if due_date and due_date != "None":
                                task_info += f" (Due: {due_date})"

                            if priority == "high":
                                high_priority.append(task_info)
                            elif priority == "medium":
                                medium_priority.append(task_info)
                            elif priority == "low":
                                low_priority.append(task_info)
                            else:
                                no_priority.append(task_info)

                    lines = ["📋 **Your Tasks**\n"]

                    if high_priority:
                        lines.append("🔴 **HIGH PRIORITY**")
                        lines.extend(high_priority)

                    if medium_priority:
                        lines.append("\n🟡 **MEDIUM PRIORITY**")
                        lines.extend(medium_priority)

                    if low_priority:
                        lines.append("\n🟢 **LOW PRIORITY**")
                        lines.extend(low_priority)

                    if no_priority:
                        lines.append("\n⚪ **NO PRIORITY**")
                        lines.extend(no_priority)

                    lines.append(f"\n_{len(list_tasks_result)} task(s) total_")
                    final_response_text = "\n".join(lines)
                    
                elif list_tasks_result is not None and len(list_tasks_result) == 0:
                    # No tasks found
                    final_response_text = "✨ No tasks found matching your criteria. Great job staying on top of things!"
                elif operation_message:
                    final_response_text = operation_message
                elif not final_response_text:
                    final_response_text = "✅ Task completed successfully."

            if not final_response_text:
                final_response_text = "✅ Task completed successfully."

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
            error_str = str(e)
            
            # Log the full error for debugging
            ai_logger.log_ai_error(
                user_id=user_id,
                conversation_id=conversation_id or "unknown",
                error_message=error_str,
                error_type=type(e).__name__,
                request_content=message
            )
            
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Agent error processing message: {error_str}", exc_info=True)
            
            # Return user-friendly error messages based on error type
            if "rate limit" in error_str.lower() or "too many requests" in error_str.lower():
                user_message = "I'm receiving too many requests right now. Please wait a moment and try again."
            elif "api key" in error_str.lower() or "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                user_message = "There's an authentication issue. Please contact support to verify the API configuration."
            elif "connection" in error_str.lower() or "timeout" in error_str.lower() or "network" in error_str.lower():
                user_message = "I'm having trouble connecting to the service. Please check your internet connection and try again."
            elif "task" in error_str.lower() and ("not found" in error_str.lower() or "doesn't exist" in error_str.lower()):
                user_message = "I couldn't find that task. It may have been deleted or doesn't exist."
            elif "permission" in error_str.lower() or "access denied" in error_str.lower():
                user_message = "You don't have permission to perform this action. Please check with the task owner."
            elif "invalid" in error_str.lower() and ("format" in error_str.lower() or "format" in error_str.lower()):
                user_message = "The information provided doesn't look quite right. Please check the format and try again."
            elif "duplicate" in error_str.lower() or "already exists" in error_str.lower():
                user_message = "This item already exists. Please try with a different name or description."
            elif "groq" in error_str.lower() and ("paused" in error_str.lower() or "access has been paused" in error_str.lower()):
                user_message = "The AI service is temporarily unavailable. Please try again in a few minutes or contact support."
            else:
                user_message = "Sorry, I encountered an unexpected error while processing your request. Please try again."
            
            return {
                "response": user_message,
                "tool_results": [],
                "success": False,
                "error": error_str  # Keep full error for debugging
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
            error_str = str(e)
            
            # Log the error for debugging
            ai_logger.log_ai_error(
                user_id=user_id,
                conversation_id="context-chat",
                error_message=error_str,
                error_type=type(e).__name__,
                request_content=message
            )
            
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Agent error processing message: {error_str}", exc_info=True)
            
            # Return user-friendly error message
            if "rate limit" in error_str.lower():
                user_message = "I'm receiving too many requests. Please wait a moment and try again."
            elif "authentication" in error_str.lower() or "api key" in error_str.lower():
                user_message = "There's an authentication issue. Please contact support."
            elif "connection" in error_str.lower() or "timeout" in error_str.lower():
                user_message = "Having trouble connecting. Please check your internet and try again."
            else:
                user_message = "Sorry, I encountered an error. Please try again."
            
            return {
                "response": user_message,
                "tool_results": [],
                "success": False,
                "error": error_str
            }


# Global AI agent instance
ai_agent_service = AIAgentService()