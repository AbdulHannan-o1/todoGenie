"""
Intent recognition module for the AI Agent service
Handles detection of various user intents and task-related requests
"""

import re
from typing import Tuple, Optional


def detect_task_list_intent(message: str) -> bool:
    """
    Detect if user is asking to list/show tasks
    """
    message_lower = message.lower().strip()

    # Check for keywords that indicate task-related intent
    task_keywords = ['task', 'tasks', 'todo', 'to-do', 'to do', 'things to do', 'items', 'list', 'pending', 'active', 'current', 'my']
    query_keywords = ['what', 'show', 'list', 'display', 'view', 'see', 'get', 'tell me', 'do i have', 'do i', 'are there']
    status_keywords = ['pending', 'active', 'current', 'incomplete', 'open', 'remaining', 'left', 'not done', 'outstanding']
    completed_keywords = ['completed', 'done', 'finished', 'completed tasks', 'done tasks', 'finished tasks', 'all done', 'all completed']

    # Count relevant keywords to determine if this is a task-related query
    task_word_count = sum(1 for word in task_keywords if word in message_lower)
    query_word_count = sum(1 for word in query_keywords if word in message_lower)
    status_word_count = sum(1 for word in status_keywords if word in message_lower)
    completed_word_count = sum(1 for word in completed_keywords if word in message_lower)

    # Determine if this is likely a task-related request based on keyword presence
    is_task_related = (
        (task_word_count > 0 and query_word_count > 0) or  # e.g., "show tasks", "list my tasks"
        (task_word_count > 0 and status_word_count > 0) or  # e.g., "show pending tasks"
        (task_word_count > 0 and completed_word_count > 0) or  # e.g., "show completed tasks"
        'what are my tasks' in message_lower or
        'what are my pending' in message_lower or
        'what are my completed' in message_lower or
        'show me my tasks' in message_lower or
        'show me my pending' in message_lower or
        'show me my completed' in message_lower or
        'list all my tasks' in message_lower or
        'list my tasks' in message_lower or
        'list completed tasks' in message_lower
    )

    return is_task_related


def detect_completed_task_specific(message: str) -> bool:
    """
    Check if specifically requesting completed tasks
    """
    message_lower = message.lower().strip()

    completed_keywords = ['completed', 'done', 'finished', 'completed tasks', 'done tasks', 'finished tasks', 'all done', 'all completed']
    completed_word_count = sum(1 for word in completed_keywords if word in message_lower)

    is_completed_specific = (
        completed_word_count > 0 or
        'completed tasks' in message_lower or
        'done tasks' in message_lower or
        'finished tasks' in message_lower or
        'show completed' in message_lower or
        'list completed' in message_lower
    )

    return is_completed_specific


def detect_task_completion_intent(message: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if user wants to complete a task and extract task number if applicable
    """
    message_lower = message.lower().strip()

    complete_keywords = ['complete', 'done', 'finish', 'mark done', 'mark as done', 'completed', 'finished', 'tick off']
    task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it', 'report', 'assignment', 'project', 'vm']

    # Count relevant keywords to determine if this is a complete task request
    complete_word_count = sum(1 for word in complete_keywords if word in message_lower)
    task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

    # Check for specific patterns indicating completion intent
    is_complete_intent = (
        complete_word_count > 0 and task_indicator_count > 0 or  # e.g., "complete task", "finish tasks"
        any(pattern in message_lower for pattern in ['complete', 'done', 'finish']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
    )

    complete_match = None
    # Check if the message contains date/time patterns first
    if is_date_or_time_pattern(message_lower):
        # If it looks like a date/time, don't treat numbers as task IDs
        complete_match = None
    else:
        # Try to extract task number only if not a date pattern
        nums = re.findall(r'\d+', message)
        if nums:
            complete_match = nums[0]

    # Check if this is a description-based completion request (no clear task ID but task-like content)
    if is_complete_intent and not complete_match:
        # Look for task descriptions in the message - if the user mentions a specific task name
        # but doesn't provide a number, we should return the message for description-based lookup
        # Extract potential task description by removing common completion phrases
        completion_phrases = ['complete ', 'finish ', 'done ', 'mark ', 'as done', 'marked as done']
        temp_msg = message_lower
        for phrase in completion_phrases:
            temp_msg = temp_msg.replace(phrase, ' ')

        # If there are words that could represent a task description, return the cleaned message
        # instead of a task ID to indicate this is a description-based request
        remaining_words = temp_msg.strip().split()
        if len([word for word in remaining_words if word not in task_indicators]) >= 2:
            # This suggests a description-based request rather than an ID-based one
            complete_match = None

    return is_complete_intent, complete_match


def detect_task_deletion_intent(message: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if user wants to delete a task and extract task number if applicable
    """
    message_lower = message.lower().strip()

    delete_keywords = ['delete', 'remove', 'erase', 'get rid of', 'eliminate', 'cancel', 'trash', 'dispose']
    task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it', 'report', 'assignment', 'project', 'vm']

    # Count relevant keywords to determine if this is a delete task request
    delete_word_count = sum(1 for word in delete_keywords if word in message_lower)
    task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

    # Check for specific patterns indicating deletion intent
    is_delete_intent = (
        delete_word_count > 0 and task_indicator_count > 0 or  # e.g., "delete task", "remove tasks"
        any(pattern in message_lower for pattern in ['delete', 'remove']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
    )

    delete_match = None
    # Check if the message contains date/time patterns first
    if is_date_or_time_pattern(message_lower):
        # If it looks like a date/time, don't treat numbers as task IDs
        delete_match = None
    else:
        # Try to extract task number only if not a date pattern
        nums = re.findall(r'\d+', message)
        if nums:
            delete_match = nums[0]

    # Check if this is a description-based deletion request (no clear task ID but task-like content)
    if is_delete_intent and not delete_match:
        # Look for task descriptions in the message - if the user mentions a specific task name
        # but doesn't provide a number, return None to indicate this is a description-based request
        # Extract potential task description by removing common deletion phrases
        deletion_phrases = ['delete ', 'remove ', 'get rid of ', 'eliminate ', 'cancel ']
        temp_msg = message_lower
        for phrase in deletion_phrases:
            temp_msg = temp_msg.replace(phrase, ' ')

        # If there are words that could represent a task description,
        # return None to indicate this is a description-based request
        remaining_words = temp_msg.strip().split()
        if len([word for word in remaining_words if word not in task_indicators]) >= 2:
            # This suggests a description-based request rather than an ID-based one
            delete_match = None

    return is_delete_intent, delete_match


def detect_task_update_intent(message: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if user wants to update a task and extract task number if applicable
    """
    message_lower = message.lower().strip()

    update_keywords = ['update', 'edit', 'change', 'modify', 'adjust', 'revise', 'alter', 'set', 'include', 'description', 'details', 'info', 'information']
    task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it', 'report', 'assignment', 'project', 'vm']

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
        # Check if the message contains date/time patterns first
        if is_date_or_time_pattern(message_lower):
            # If it looks like a date/time, don't treat numbers as task IDs
            update_match = None
        else:
            # Try to extract task number only if not a date pattern
            nums = re.findall(r'\d+', message)
            if nums:
                update_match = nums[0]

    return is_update_intent, update_match


def detect_task_update_by_name_intent(message: str) -> bool:
    """
    Detect if user wants to update a task by name rather than number
    """
    message_lower = message.lower().strip()

    update_keywords = ['update', 'edit', 'change', 'modify', 'adjust', 'revise', 'alter', 'set', 'include', 'description', 'details', 'info', 'information']
    task_indicators = ['task', 'tasks', 'item', 'items', 'thing', 'things', 'it', 'report', 'assignment', 'project', 'vm']

    # Count relevant keywords to determine if this is an update task request
    update_word_count = sum(1 for word in update_keywords if word in message_lower)
    task_indicator_count = sum(1 for word in task_indicators if word in message_lower)

    # Check for specific patterns indicating update intent
    is_update_intent = (
        update_word_count > 0 and task_indicator_count > 0 or  # e.g., "update task", "edit tasks"
        any(pattern in message_lower for pattern in ['update', 'edit', 'change', 'modify']) and any(indicator in message_lower for indicator in ['task', 'tasks'])
    )

    # Exclude cases where it's clearly a new task creation
    is_creation_intent = any(p in message_lower for p in ['create', 'add new', 'new task'])

    return is_update_intent and not is_creation_intent


def is_date_or_time_pattern(msg: str) -> bool:
    """
    Helper function to detect date/time patterns to avoid misinterpreting them as task IDs
    """
    message_lower = msg.lower()

    # Check for common date patterns: MM/DD, DD/MM, Month DD, DD Month, etc.
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}\b',  # MM/DD or DD/MM
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b',  # Month DD
        r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b',  # DD Month
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',  # Full month DD
        r'\b\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',  # DD Full month
        r'\b\d{1,2}(?:st|nd|rd|th)?\s*(?:of)?\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)\b',  # 1st Jan, 2nd of Feb, etc.
        r'\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?\b',  # HH:MM format
        r'\b\d{1,2}(?:am|pm|AM|PM)\b',  # HH AM/PM format
    ]
    for pattern in date_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    return False


def extract_task_description_from_message(message: str, task_num: str = None) -> Optional[str]:
    """
    Extract description from message (everything after common patterns)
    """
    desc = message

    # 1. If task_num was provided, handle it FIRST to avoid description indicators (like 'to')
    # appearing earlier in the message than the task reference
    if task_num:
        # Split by the task number reference
        parts = re.split(rf'task\s*{task_num}[\s,]*', desc, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) > 1:
            desc = parts[1].strip()

        # Clean up common prefixes that follow task references (longest first to avoid partial matches)
        prefixes = ['to include', 'to have', 'containing', 'should', 'will', 'with', 'to']
        for prefix in prefixes:
            if desc.lower().startswith(prefix):
                desc = desc[len(prefix):].strip()
                break

    # 2. Look for common description indicators if we haven't found a clean description yet
    # We use more specific patterns (requiring :) for keyword indicators to avoid over-matching
    for pattern in [
        r'(?:description|details|notes|info|is|for|about)[:\s]*:',
        r':\s+',
    ]:
        # Only split if the pattern is NOT at the very beginning
        parts = re.split(pattern, desc, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) > 1 and parts[0].strip():
            desc = parts[1].strip()
            break

    # Remove leading/trailing punctuation and whitespace
    desc = re.sub(r'^[:\-,\s]+', '', desc)
    desc = re.sub(r'[:\-,\s]+$', '', desc)
    desc = desc.strip()

    # Only return if the description is substantial (more than 5 characters)
    if len(desc) > 5:
        return desc
    else:
        return None

def detect_completion_statement_intent(message: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if user is describing completion of a specific task using natural language.
    Returns: (is_completion_statement, extracted_task_description)
    
    Examples:
    - "i successfully got the free vm from oracle" → (True, "free vm from oracle")
    - "i prepared for eid" → (True, "prepared for eid")
    - "i purchased the paid copilot cli" → (True, "paid copilot cli")
    - "just finished my assignment" → (True, "my assignment")
    """
    message_lower = message.lower().strip()
    
    # Patterns for completion statements
    completion_patterns = [
        # "I [verb] [object]" patterns
        r"^i\s+(?:have\s+)?(?:successfully\s+)?(?:got|completed|finished|done|purchased|prepared|deployed|submitted|acquired|done with|finished with)\s+(.+)$",
        r"^i\s+(?:just\s+)?(?:got|completed|finished|done|purchased|prepared|deployed|submitted|acquired)\s+(.+)$",
        
        # "[Object] is done/completed" patterns
        r"^(?:the\s+)?(.+?)\s+(?:is\s+)?(?:done|completed|finished|ready)$",
        
        # "finally/just [verb]" patterns
        r"^(?:just|finally|already)\s+(?:got|completed|finished|done|purchased|prepared|deployed|submitted|acquired)\s+(?:the\s+)?(.+)$",
        
        # "done with [object]" patterns
        r"^(?:i'm\s+)?done\s+with\s+(?:the\s+)?(.+)$",
        r"^(?:i'm\s+)?finished\s+with\s+(?:the\s+)?(.+)$",
        
        # Simple statements
        r"^(?:got|completed|finished|purchased|prepared|deployed|submitted)\s+(?:the\s+)?(.+)$",
    ]
    
    for pattern in completion_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            task_description = match.group(1).strip()
            # Filter out common non-task endings
            task_description = re.sub(r'\s+(?:today|yesterday|now|just|already)$', '', task_description)
            
            if len(task_description) > 3:  # At least 3 characters
                return True, task_description
    
    return False, None
