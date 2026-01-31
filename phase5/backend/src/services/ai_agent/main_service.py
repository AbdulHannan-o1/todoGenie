"""
Main AI Agent service implementation using modular components
"""
import asyncio
import time
import json
from typing import Dict, Any, Optional
from src.core.logging import ai_logger, performance_monitor
from src.models.conversation import MessageCreate
from .provider_manager import ProviderManager
from .intent_recognition import (
    detect_task_list_intent, detect_completed_task_specific,
    detect_task_completion_intent, detect_task_deletion_intent,
    detect_task_update_intent, detect_task_update_by_name_intent,
    is_date_or_time_pattern, extract_task_description_from_message
)
from .tool_integration import get_available_tools, execute_tool
from .conversation_context import (
    prepare_contextual_messages, format_task_list_response,
    log_conversation_interaction
)


class AIAgentService:
    def __init__(self):
        # Initialize provider manager
        self.provider_manager = ProviderManager()

    @property
    def current_client(self):
        return self.provider_manager.current_client

    @property
    def current_model(self):
        return self.provider_manager.current_model

    @property
    def current_provider(self):
        return self.provider_manager.current_provider

    def switch_to_backup(self):
        """Switch to backup provider (Bonsai)"""
        self.provider_manager.switch_to_backup()

    def switch_to_primary(self):
        """Switch back to primary provider (Groq)"""
        self.provider_manager.switch_to_primary()

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
        is_task_related = detect_task_list_intent(message)

        # Check if specifically requesting completed tasks
        is_completed_specific = detect_completed_task_specific(message)

        # Instead of handling task listing directly, let the AI model use the list_tasks tool via MCP server

        # Check if user wants to complete a task
        is_complete_intent, complete_match = detect_task_completion_intent(message)

        # Instead of handling completions directly, let the AI model use the complete_task tool via MCP server

        # Check if user wants to delete a task
        is_delete_intent, delete_match = detect_task_deletion_intent(message)

        # Instead of handling deletes directly, let the AI model use the delete_task tool via MCP server

        # Instead of handling updates directly in the agent, let the AI model use the update_task tool
        # which can handle all types of updates dynamically (title, description, due_date, priority, etc.)
        # The AI will analyze the user's request and call the appropriate tools as needed

        try:
            # Get the tools available to the AI agent
            tools = get_available_tools()

            # Prepare the system message to guide the AI's behavior
            system_message = {
                "role": "system",
                "content": (
                    "You are a friendly AI companion and task manager. Your personality is empathetic, supportive, and helpful like a close friend. You can help with anything - just ask!\n\n"

                    "CORE IDENTITY:\n"
                    "- Be warm, conversational, and genuinely caring\n"
                    "- Listen actively and offer helpful suggestions\n"
                    "- Seamlessly blend friendship with task management\n\n"

                    "TASK MANAGEMENT CAPABILITIES:\n"
                    "You can create, list, update, delete, complete tasks, and manage advanced features using these tools:\n"
                    "- create_task: Create new tasks (also triggered by 'add', 'make', 'create')\n"
                    "- list_tasks: Show current tasks\n"
                    "- update_task: Modify existing tasks\n"
                    "- delete_task: Remove tasks\n"
                    "- complete_task: Mark tasks as done\n\n"

                    "ADVANCED FEATURES:\n"
                    "You can also manage these advanced features:\n"
                    "- Recurring tasks: Set up tasks that repeat daily, weekly, monthly, or yearly\n"
                    "- Due date reminders: Set specific times to be reminded about tasks\n"
                    "- Tags and categories: Organize tasks with customizable tags\n"
                    "- Hierarchical tasks: Create parent tasks with sub-tasks for better organization\n\n"

                    "CONVERSATIONAL INTELLIGENCE:\n"
                    "- Engage in friendly chat about life, problems, goals\n"
                    "- Detect when user mentions tasks during conversation\n"
                    "- Recognize various ways users might ask about tasks:\n"
                    "  * 'what are my tasks', 'show me pending tasks', 'list my tasks', 'what do I have to do'\n"
                    "- Extract tasks from natural conversation:\n"
                    "  * Identify due dates ('tomorrow', 'next week', 'by Friday')\n"
                    "  * Recognize priorities ('urgent', 'important', 'when possible')\n"
                    "  * Understand task details embedded in stories\n"
                    "  * Detect when user wants recurring tasks ('every day', 'weekly', 'monthly')\n"
                    "  * Recognize when user wants to set reminders ('remind me', 'notification')\n"
                    "  * Identify when user wants to categorize tasks ('tag with', 'category', 'labels')\n"
                    "  * Understand hierarchical relationships ('sub-task of', 'child of', 'parent task')\n\n"

                    "TASK CREATION GUIDELINES:\n"
                    "- title: Main task (extract from conversation)\n"
                    "- description: Details (derive from context)\n"
                    "- priority: low, medium, high, or urgent (infer from urgency words)\n"
                    "- due_date: ISO format (convert from natural language)\n"
                    "- reminder_time: Specific time to be notified (derive from reminder requests)\n"
                    "- tags: Comma-separated categories (derive from context)\n"
                    "- recurrence_pattern: How often the task repeats (daily, weekly, monthly, yearly)\n"
                    "- parent_task_id: ID of parent task if this is a sub-task\n\n"

                    "TASK LISTING FORMAT:\n"
                    "| # | Name | Due Date | Priority | Tags | Recurrence | Parent |\n"
                    "|---|------|----------|----------|------|------------|--------|\n"
                    "| 1 | Buy coffee | 2025-01-15 | high | shopping | daily | - |\n\n"

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

                    "When user shares concerns (like being late), acknowledge their feelings first, then suggest helpful actions like task management to prevent future issues. Remember, you're here to help with whatever the user needs!"
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
                    function_args = {}
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except:
                        function_args = {}

                    # Handle null arguments (for functions that don't require args like list_tasks)
                    if function_args is None:
                        function_args = {}

                    # Execute the tool
                    result = execute_tool(function_name, function_args, user_id)

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
                    final_response_text = format_task_list_response(list_tasks_result)
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
            # Use conversation history if available
            if conversation_history:
                # Prepare messages for the AI including conversation history
                system_prompt = (
                    "You are a friendly AI companion and task manager. Your personality is empathetic, supportive, and helpful like a close friend. You can help with anything - just ask!\n\n"

                    "CORE IDENTITY:\n"
                    "- Be warm, conversational, and genuinely caring\n"
                    "- Listen actively and offer helpful suggestions\n"
                    "- Seamlessly blend friendship with task management\n\n"

                    "TASK MANAGEMENT CAPABILITIES:\n"
                    "You can create, list, update, delete, complete tasks, and manage advanced features using these tools:\n"
                    "- create_task: Create new tasks (also triggered by 'add', 'make', 'create')\n"
                    "- list_tasks: Show current tasks\n"
                    "- update_task: Modify existing tasks\n"
                    "- delete_task: Remove tasks\n"
                    "- complete_task: Mark tasks as done\n\n"

                    "ADVANCED FEATURES:\n"
                    "You can also manage these advanced features:\n"
                    "- Recurring tasks: Set up tasks that repeat daily, weekly, monthly, or yearly\n"
                    "- Due date reminders: Set specific times to be reminded about tasks\n"
                    "- Tags and categories: Organize tasks with customizable tags\n"
                    "- Hierarchical tasks: Create parent tasks with sub-tasks for better organization\n\n"

                    "CONVERSATIONAL INTELLIGENCE:\n"
                    "- Engage in friendly chat about life, problems, goals\n"
                    "- Detect when user mentions tasks during conversation\n"
                    "- Recognize various ways users might ask about tasks:\n"
                    "  * 'what are my tasks', 'show me pending tasks', 'list my tasks', 'what do I have to do'\n"
                    "- Extract tasks from natural conversation:\n"
                    "  * Identify due dates ('tomorrow', 'next week', 'by Friday')\n"
                    "  * Recognize priorities ('urgent', 'important', 'when possible')\n"
                    "  * Understand task details embedded in stories\n"
                    "  * Detect when user wants recurring tasks ('every day', 'weekly', 'monthly')\n"
                    "  * Recognize when user wants to set reminders ('remind me', 'notification')\n"
                    "  * Identify when user wants to categorize tasks ('tag with', 'category', 'labels')\n"
                    "  * Understand hierarchical relationships ('sub-task of', 'child of', 'parent task')\n\n"

                    "TASK CREATION GUIDELINES:\n"
                    "- title: Main task (extract from conversation)\n"
                    "- description: Details (derive from context)\n"
                    "- priority: low, medium, high, or urgent (infer from urgency words)\n"
                    "- due_date: ISO format (convert from natural language)\n"
                    "- reminder_time: Specific time to be notified (derive from reminder requests)\n"
                    "- tags: Comma-separated categories (derive from context)\n"
                    "- recurrence_pattern: How often the task repeats (daily, weekly, monthly, yearly)\n"
                    "- parent_task_id: ID of parent task if this is a sub-task\n\n"

                    "TASK LISTING FORMAT:\n"
                    "| # | Name | Due Date | Priority | Tags | Recurrence | Parent |\n"
                    "|---|------|----------|----------|------|------------|--------|\n"
                    "| 1 | Buy coffee | 2025-01-15 | high | shopping | daily | - |\n\n"

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

                    "When user shares concerns (like being late), acknowledge their feelings first, then suggest helpful actions like task management to prevent future issues. Remember, you're here to help with whatever the user needs!"

                    "\n\nPrevious conversation context:\n"
                )

                messages = prepare_contextual_messages(
                    system_prompt,
                    conversation_history,
                    message
                )

                # Get the tools available to the AI agent
                tools = get_available_tools()

                # Agentic loop: keep calling the AI until it stops making tool calls
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
                                conversation_id="context-chat",
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
                        function_args = {}
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except:
                            function_args = {}

                        # Handle null arguments (for functions that don't require args like list_tasks)
                        if function_args is None:
                            function_args = {}

                        # Execute the tool
                        result = execute_tool(function_name, function_args, user_id)

                        # Log tool execution
                        # Determine success based on whether result is a dict with status != "error"
                        # or if it's a list (like from list_tasks), assume success
                        is_success = True
                        if isinstance(result, dict):
                            is_success = result.get("status") != "error"
                        # For lists (like from list_tasks), we consider it successful if no exception occurred

                        ai_logger.log_tool_execution(
                            user_id=user_id,
                            conversation_id="context-chat",
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
                        final_response_text = format_task_list_response(list_tasks_result)
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
                    conversation_id="context-chat",
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
            else:
                # If no conversation history, fall back to basic process_message
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