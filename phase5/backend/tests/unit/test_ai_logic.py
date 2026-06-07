import pytest
from src.services.ai_agent.intent_recognition import (
    detect_task_list_intent,
    detect_task_completion_intent,
    detect_task_deletion_intent,
    detect_task_update_intent,
    detect_completion_statement_intent,
    extract_task_description_from_message
)
from src.services.ai_agent.conversation_context import (
    prepare_contextual_messages,
    format_task_list_response
)

def test_detect_task_list_intent():
    assert detect_task_list_intent("show my tasks") is True
    assert detect_task_list_intent("what's on my list?") is True
    assert detect_task_list_intent("hello there") is False
    assert detect_task_list_intent("list completed tasks") is True

def test_detect_task_completion_intent():
    # ID based
    is_intent, task_num = detect_task_completion_intent("complete task 5")
    assert is_intent is True
    assert task_num == "5"
    
    # Description based (semantic)
    is_intent, task_num = detect_task_completion_intent("i finished the report")
    assert is_intent is True
    assert task_num is None # Numbers in dates shouldn't count
    
    # Date pattern exclusion
    is_intent, task_num = detect_task_completion_intent("complete by 12/12")
    assert task_num is None

def test_detect_completion_statement_intent():
    is_stmt, desc = detect_completion_statement_intent("i successfully got the free vm from oracle")
    assert is_stmt is True
    assert desc == "the free vm from oracle"
    
    is_stmt, desc = detect_completion_statement_intent("just finished my assignment")
    assert is_stmt is True
    assert desc == "my assignment"

def test_extract_task_description():
    msg = "update task 5 to include new details about the project"
    desc = extract_task_description_from_message(msg, "5")
    assert desc == "new details about the project"
    
    msg = "set description for task 1 to: buy more milk"
    desc = extract_task_description_from_message(msg, "1")
    assert desc == "buy more milk"

def test_prepare_contextual_messages():
    system_prompt = "You are a helpful assistant."
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
    current = "What is my name?"
    
    messages = prepare_contextual_messages(system_prompt, history, current)
    
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == current

def test_format_task_list_response():
    tasks = [
        {"title": "Critical Task", "priority": "high", "due_date": "2024-12-01T10:00:00"},
        {"title": "Normal Task", "priority": "medium"},
        {"title": "Easy Task", "priority": "low"}
    ]
    
    response = format_task_list_response(tasks)
    assert "Critical Task" in response
    assert "HIGH PRIORITY" in response
    assert "MEDIUM PRIORITY" in response
    assert "LOW PRIORITY" in response
    assert "Due: 2024-12-01" in response

def test_format_empty_task_list():
    assert "no pending tasks" in format_task_list_response([]).lower()
