"""
AI Agent service for processing natural language commands with primary (Bonsai) and backup (Groq) providers
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
            message_type="text"
        )

        # Check if user is asking to list/show tasks - handle directly
        message_lower = message.lower().strip()

        # Enhanced semantic understanding for task-related requests
        # Check for keywords that indicate task-related intent
        task_keywords = ['task', 'tasks', 'todo', 'to-do', 'to do', 'things to do', 'items', 'list', 'pending', 'active', 'current', 'my']
        query_keywords = ['what', 'show', 'list', 'display', 'view', 'see', 'get', 'tell me', 'do i have', 'do i', 'are there']
        status_keywords = ['pending', 'active', 'current', 'incomplete', 'open', 'remaining', 'left', 'not done', 'outstanding']

        # Count relevant keywords to determine if this is a task-related query
        task_word_count = sum(1 for word in task_keywords if word in message_lower)
        query_word_count = sum(1 for word in query_keywords if word in message_lower)
        status_word_count = sum(1 for word in status_keywords if word in message_lower)

        # Determine if this is likely a task-related request based on keyword presence
        is_task_related = (
            (task_word_count > 0 and query_word_count > 0) or  # e.g., "show tasks", "list my tasks"
            (task_word_count > 0 and status_word_count > 0) or  # e.g., "show pending tasks"
            'what are my tasks' in message_lower or
            'what are my pending' in message_lower or
            'show me my tasks' in message_lower or
            'show me my pending' in message_lower or
            'list all my tasks' in message_lower or
            'list my tasks' in message_lower
        )

        if is_task_related:
            from src.services.mcp_server.todo_tools import list_tasks_tool
            tasks = list_tasks_tool(user_id=user_id)

            if isinstance(tasks, list) and len(tasks) > 0:
                high_priority = []
                medium_priority = []
                low_priority = []
                no_priority = []

                for task in tasks:
                    if isinstance(task, dict):
                        title = task.get("title", "Untitled")
                        due_date = task.get("due_date")
                        if due_date and isinstance(due_date, str) and "T" in due_date:
                            due_date = due_date.split("T")[0]
                        priority = task.get("priority", "").lower() if task.get("priority") else ""

                        task_info = f"• {title}"
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

                lines = ["📋 **Your Pending Tasks**\n"]

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
                    lines.append("\n⚪ **NO PRIORITY SET**")
                    lines.extend(no_priority)

                lines.append(f"\n_{len(tasks)} task(s) total_")
                final_response = "\n".join(lines)
            else:
                final_response = "✨ You have no pending tasks. Great job!"

            return {
                "response": final_response,
                "tool_results": tasks if isinstance(tasks, list) else [],
                "success": True
            }

        # Check if user wants to complete a task
        # Enhanced semantic understanding for complete task requests
        complete_keywords = ['complete', 'done', 'finish', 'mark done', 'mark as done', 'completed', 'finished', 'tick off']
        task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it']

        # Count relevant keywords to determine if this is a complete task request
        complete_word_count = sum(1 for word in complete_keywords if word in message_lower)
        task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

        # Check for specific patterns indicating completion intent
        is_complete_intent = (
            complete_word_count > 0 and task_indicator_count > 0 or  # e.g., "complete task", "finish tasks"
            any(pattern in message_lower for pattern in ['complete', 'done', 'finish']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
        )

        import re
        complete_match = None
        if is_complete_intent:
            # Try to extract task number
            nums = re.findall(r'\d+', message)
            if nums:
                complete_match = nums[0]

        if complete_match and not any(p in message_lower for p in ['create', 'add new', 'new task']):
            from src.services.mcp_server.todo_tools import list_tasks_tool, complete_task_tool

            tasks = list_tasks_tool(user_id=user_id)
            if isinstance(tasks, list) and len(tasks) > 0:
                task_idx = int(complete_match) - 1
                if 0 <= task_idx < len(tasks):
                    task = tasks[task_idx]
                    task_id = task.get('id') if isinstance(task, dict) else None
                    if task_id:
                        result = complete_task_tool(task_id=task_id, completed=True)
                        if isinstance(result, dict) and result.get('status') == 'success':
                            task_title = task.get('title', 'Task')
                            final_response = f"✅ Completed \"{task_title}\""
                        else:
                            final_response = "❌ Failed to complete task"
                    else:
                        final_response = "❌ Could not find task ID"
                else:
                    final_response = f"❌ Task {complete_match} not found"
            else:
                final_response = "No tasks found"

            return {
                "response": final_response,
                "tool_results": [],
                "success": True
            }

        # Check if user wants to delete a task
        # Enhanced semantic understanding for delete task requests
        delete_keywords = ['delete', 'remove', 'erase', 'get rid of', 'eliminate', 'cancel', 'trash', 'dispose']
        task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it']

        # Count relevant keywords to determine if this is a delete task request
        delete_word_count = sum(1 for word in delete_keywords if word in message_lower)
        task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

        # Check for specific patterns indicating deletion intent
        is_delete_intent = (
            delete_word_count > 0 and task_indicator_count > 0 or  # e.g., "delete task", "remove tasks"
            any(pattern in message_lower for pattern in ['delete', 'remove']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
        )

        delete_match = None
        if is_delete_intent:
            nums = re.findall(r'\d+', message)
            if nums:
                delete_match = nums[0]

        if delete_match and not any(p in message_lower for p in ['create', 'add new', 'new task']):
            from src.services.mcp_server.todo_tools import list_tasks_tool, delete_task_tool

            tasks = list_tasks_tool(user_id=user_id)
            if isinstance(tasks, list) and len(tasks) > 0:
                task_idx = int(delete_match) - 1
                if 0 <= task_idx < len(tasks):
                    task = tasks[task_idx]
                    task_id = task.get('id') if isinstance(task, dict) else None
                    if task_id:
                        result = delete_task_tool(task_id=task_id)
                        if isinstance(result, dict) and result.get('status') == 'success':
                            task_title = task.get('title', 'Task')
                            final_response = f"🗑️ Deleted \"{task_title}\""
                        else:
                            final_response = "❌ Failed to delete task"
                    else:
                        final_response = "❌ Could not find task ID"
                else:
                    final_response = f"❌ Task {delete_match} not found"
            else:
                final_response = "No tasks found"

            return {
                "response": final_response,
                "tool_results": [],
                "success": True
            }

        # Check if user wants to update a task
        # Enhanced semantic understanding for update task requests
        update_keywords = ['update', 'edit', 'change', 'modify', 'adjust', 'revise', 'alter', 'set', 'add', 'include', 'description', 'details', 'info', 'information']
        task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it']

        # Count relevant keywords to determine if this is an update task request
        update_word_count = sum(1 for word in update_keywords if word in message_lower)
        task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

        # Check for specific patterns indicating update intent
        is_update_intent = (
            update_word_count > 0 and task_indicator_count > 0 or  # e.g., "update task", "edit tasks"
            any(pattern in message_lower for pattern in ['update', 'edit', 'change', 'modify']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
        )

        update_match = None
        if is_update_intent:
            nums = re.findall(r'\d+', message)
            if nums:
                update_match = nums[0]

        if update_match and not any(p in message_lower for p in ['create', 'add new', 'new task']):
            # Handle "task X" format
            from src.services.mcp_server.todo_tools import list_tasks_tool, update_task_tool

            tasks = list_tasks_tool(user_id=user_id)
            if isinstance(tasks, list) and len(tasks) > 0:
                task_idx = int(update_match) - 1
                if 0 <= task_idx < len(tasks):
                    task = tasks[task_idx]
                    task_id = task.get('id') if isinstance(task, dict) else None
                    if task_id:
                        # Extract description
                        desc_match = re.search(r'(?:description|details?|more info)[:\s]+(.+)', message_lower)
                        if not desc_match:
                            parts = re.split(rf'task\s*{update_match}', message, maxsplit=1, flags=re.IGNORECASE)
                            if len(parts) > 1:
                                desc = parts[1].strip()
                                for prefix in ['to include', 'with', 'to have', 'containing']:
                                    if desc.startswith(prefix):
                                        desc = desc[len(prefix):].strip()
                                if len(desc) > 5:
                                    desc_match = desc

                        description = None
                        if desc_match:
                            description = desc_match.strip() if isinstance(desc_match, str) else desc_match.group(1).strip()

                        if description:
                            result = update_task_tool(task_id=task_id, description=description)
                            if isinstance(result, dict) and result.get('status') == 'success':
                                task_title = task.get('title', 'Task')
                                final_response = f"✏️ Updated description for \"{task_title}\""
                            else:
                                final_response = "❌ Failed to update task"
                        else:
                            final_response = "❌ Please specify what description to add"
                    else:
                        final_response = "❌ Could not find task ID"
                else:
                    final_response = f"❌ Task {update_match} not found"
            else:
                final_response = "No tasks found"

            return {
                "response": final_response,
                "tool_results": [],
                "success": True
            }

        # Handle update by task name (e.g., "update debug error task in docker")
        if is_update_intent and not any(p in message_lower for p in ['create', 'add new', 'new task']):
            from src.services.mcp_server.todo_tools import list_tasks_tool, update_task_tool

            tasks = list_tasks_tool(user_id=user_id)
            if isinstance(tasks, list) and len(tasks) > 0:
                # Try to find task by partial name match
                target_task = None
                for task in tasks:
                    if isinstance(task, dict):
                        title = task.get('title', '').lower()
                        # Check if any key words from message match task title
                        words = re.findall(r'\b\w+\b', message_lower)
                        for word in words:
                            if len(word) > 3 and word in title:
                                target_task = task
                                break
                    if target_task:
                        break

                if target_task:
                    task_id = target_task.get('id')
                    # Extract description from message (everything after common patterns)
                    desc = message
                    for prefix in ['update', 'edit', 'change', 'modify', 'set description', 'update description', 'for']:
                        if desc.lower().startswith(prefix):
                            desc = desc[len(prefix):].strip()
                            break

                    # Remove task name from description
                    task_name = target_task.get('title', '')
                    desc = desc.replace(task_name, '').strip()
                    for prefix in ['task', 'to', 'with', 'to include', 'containing']:
                        desc = re.sub(rf'^{prefix}\s*', '', desc, flags=re.IGNORECASE).strip()

                    description = desc if len(desc) > 5 else None

                    if description:
                        result = update_task_tool(task_id=task_id, description=description)
                        if isinstance(result, dict) and result.get('status') == 'success':
                            task_title = target_task.get('title', 'Task')
                            final_response = f"✏️ Updated description for \"{task_title}\""
                        else:
                            final_response = "❌ Failed to update task"
                    else:
                        final_response = "❌ Please specify what description to add"
                else:
                    final_response = "❌ Could not find the task you want to update"
            else:
                final_response = "No tasks found"

            return {
                "response": final_response,
                "tool_results": [],
                "success": True
            }

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
                    "You are a friendly AI companion and task manager. Your personality is empathetic, supportive, and helpful like a close friend.\n\n"

                    "CORE IDENTITY:\n"
                    "- Be warm, conversational, and genuinely caring\n"
                    "- Listen actively and offer helpful suggestions\n"
                    "- Seamlessly blend friendship with task management\n\n"

                    "TASK MANAGEMENT CAPABILITIES:\n"
                    "You can create, list, update, delete, and complete tasks using these tools:\n"
                    "- create_task: Create new tasks\n"
                    "- list_tasks: Show current tasks\n"
                    "- update_task: Modify existing tasks\n"
                    "- delete_task: Remove tasks\n"
                    "- complete_task: Mark tasks as done\n\n"

                    "CONVERSATIONAL INTELLIGENCE:\n"
                    "- Engage in friendly chat about life, problems, goals\n"
                    "- Detect when user mentions tasks during conversation\n"
                    "- Recognize various ways users might ask about tasks:\n"
                    "  * 'what are my tasks', 'show me pending tasks', 'list my tasks', 'what do I have to do'\n"
                    "- Extract tasks from natural conversation:\n"
                    "  * Identify due dates ('tomorrow', 'next week', 'by Friday')\n"
                    "  * Recognize priorities ('urgent', 'important', 'when possible')\n"
                    "  * Understand task details embedded in stories\n\n"

                    "TASK CREATION GUIDELINES:\n"
                    "- title: Main task (extract from conversation)\n"
                    "- description: Details (derive from context)\n"
                    "- priority: low, medium, or high (infer from urgency words)\n"
                    "- due_date: ISO format (convert from natural language)\n"
                    "- tags: Categories (derive from context)\n\n"

                    "TASK LISTING FORMAT:\n"
                    "| # | Name | Due Date | Priority |\n"
                    "|---|------|----------|----------|\n"
                    "| 1 | Buy coffee | 2025-01-15 | high |\n\n"

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

                            task_info = f"• {title}"
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

                    lines = ["📋 **Your Pending Tasks**\n"]

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
                        lines.append("\n⚪ **NO PRIORITY SET**")
                        lines.extend(no_priority)

                    lines.append(f"\n_{len(list_tasks_result)} task(s) total_")
                    final_response_text = "\n".join(lines)
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