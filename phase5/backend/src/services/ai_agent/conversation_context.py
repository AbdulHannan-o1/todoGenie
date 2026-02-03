"""
Conversation context module for the AI Agent service
Handles conversation history management and context-aware responses
"""

import time
from typing import Dict, Any, List, Optional
from src.core.logging import ai_logger


def prepare_contextual_messages(
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    current_message: str
) -> List[Dict[str, str]]:
    """
    Prepare messages for the AI including conversation history
    """
    messages = []

    # Add system message first
    system_message = {
        "role": "system",
        "content": system_prompt
    }
    messages.append(system_message)

    # Add conversation history to messages
    recent_history = conversation_history[-25:] if len(conversation_history) > 25 else conversation_history  # Limit to last 25 messages

    for hist_item in recent_history:
        # Convert history item to appropriate role and content
        role = hist_item.get('role', 'user')  # Default to 'user' if not specified
        content = hist_item.get('content', hist_item.get('text', str(hist_item)))

        # Ensure role is properly formatted
        if role.lower() in ['user', 'human', 'person']:
            role = 'user'
        elif role.lower() in ['assistant', 'bot', 'ai', 'system']:
            role = 'assistant'
        else:
            # Default to user if unknown role
            role = 'user'

        messages.append({
            "role": role,
            "content": content
        })

    # Add the current user message
    messages.append({
        "role": "user",
        "content": current_message
    })

    return messages


def format_task_list_response(task_list: List[Dict[str, Any]]) -> str:
    """
    Format a list of tasks into a readable response
    """
    if not task_list:
        return "✨ You have no pending tasks. Great job!"

    # Group tasks by priority
    high_priority = []
    medium_priority = []
    low_priority = []
    no_priority = []

    for task in task_list:
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

    lines.append(f"\n_{len(task_list)} task(s) total_")
    return "\n".join(lines)


def log_conversation_interaction(
    user_id: str,
    conversation_id: str,
    message: str,
    response: str,
    start_time: float,
    success: bool = True,
    tool_results: List[Dict[str, Any]] = None
) -> None:
    """
    Log the AI response for the conversation
    """
    if tool_results is None:
        tool_results = []

    processing_time = time.time() - start_time

    # Log the AI response
    ai_logger.log_ai_response(
        user_id=user_id,
        conversation_id=conversation_id,
        request_content=message,
        response_content=response,
        processing_time=processing_time,
        success=success,
        tool_results=tool_results
    )