# AI Agent Implementation Fix Plan

## Executive Summary

**Current State**: The AI agent has hardcoded keyword detection (lines 85-400 in `ai_agent.py`) that bypasses the LLM entirely. Conversation history is saved to DB but never passed to the LLM. This makes the agent feel "dumb" and unresponsive to specific questions.

**Target State**: Per hackathon spec, the LLM should interpret all user intent, have access to conversation history, and call MCP tools autonomously.

---

## Phase 1: Foundation - Remove Hardcoded Logic

### Task 1.1: Delete Hardcoded Keyword Detection
**File**: `phase3/backend/src/services/ai_agent.py`
**Lines**: 85-400 (approximately 315 lines)

**Action**: Remove these code blocks:
- Lines 85-155: `is_task_related` detection and early return
- Lines 157-210: `is_complete_intent` detection and early return
- Lines 212-265: `is_delete_intent` detection and early return
- Lines 267-335: `is_update_intent` detection (first block)
- Lines 335-400: `is_update_intent` detection (second block - by task name)

**Keep**: Lines 1-84 (imports, class definition, provider config) and lines 401+ (actual LLM call)

**Acceptance Criteria**:
- [ ] `process_message()` method goes directly to LLM call
- [ ] No keyword matching in Python code
- [ ] All intent interpretation delegated to LLM

---

### Task 1.2: Add Conversation History Fetching
**File**: `phase3/backend/src/services/ai_agent.py`

**Current Code** (line ~543):
```python
messages = [system_message, user_message]
```

**New Code**:
```python
# Fetch conversation history from database
conversation_history = await self._get_conversation_history(
    conversation_id=conversation_id,
    user_id=user_id,
    max_messages=10  # Last 10 messages for context
)

# Build messages array with history
messages = [system_message] + conversation_history + [user_message]
```

**New Method to Add**:
```python
async def _get_conversation_history(
    self,
    conversation_id: Optional[str],
    user_id: str,
    max_messages: int = 10
) -> List[Dict[str, str]]:
    """
    Fetch last N messages from conversation history.
    Returns list of {role, content} dicts for LLM.
    """
    if not conversation_id:
        return []
    
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
        
        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
```

**Acceptance Criteria**:
- [ ] New method `_get_conversation_history()` exists
- [ ] Fetches last 10 messages from DB
- [ ] Messages formatted as `{role, content}` for LLM
- [ ] Empty list returned if no conversation_id
- [ ] Messages inserted between system prompt and current user message

---

## Phase 2: Tool Enhancements

### Task 2.1: Add `get_task_details` Tool
**File**: `phase3/backend/src/services/mcp_server/todo_tools.py`

**Add New Function**:
```python
def get_task_details_tool(task_id: str, user_id: str = "") -> Dict:
    """
    Get detailed information about a specific task
    """
    return TaskOperationsService.get_task_details(task_id, user_id)
```

**File**: `phase3/backend/src/services/task_operations.py`

**Add New Method**:
```python
@staticmethod
def get_task_details(task_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific task
    """
    try:
        with next(get_session()) as session:
            task = session.get(Task, UUID(task_id))
            
            if not task:
                return {
                    "status": "error",
                    "message": f"Task {task_id} not found"
                }
            
            # Verify ownership
            if str(task.user_id) != user_id:
                return {
                    "status": "error",
                    "message": "Access denied: Task does not belong to user"
                }
            
            return {
                "status": "success",
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get task details: {str(e)}"
        }
```

**Acceptance Criteria**:
- [ ] `get_task_details_tool()` in `todo_tools.py`
- [ ] `get_task_details()` in `task_operations.py`
- [ ] Returns full task details including priority, tags, dates
- [ ] Verifies user ownership
- [ ] Returns error if task not found

---

### Task 2.2: Add Filtering to `list_tasks`
**File**: `phase3/backend/src/services/task_operations.py`

**Current Signature**:
```python
def list_tasks(user_id: str) -> Dict[str, Any]:
```

**New Signature**:
```python
def list_tasks(
    user_id: str,
    status: Optional[str] = None,  # "pending", "completed", "all"
    priority: Optional[str] = None,  # "high", "medium", "low"
    tags: Optional[str] = None,  # comma-separated
    search: Optional[str] = None  # keyword search
) -> Dict[str, Any]:
```

**Implementation**:
```python
@staticmethod
def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    List tasks for user with optional filters
    """
    try:
        with next(get_session()) as session:
            user_uuid = UUID(user_id)
            
            # Build query
            statement = select(Task).where(Task.user_id == user_uuid)
            
            # Apply filters
            if status and status != "all":
                is_completed = status.lower() == "completed"
                statement = statement.where(Task.completed == is_completed)
            
            if priority:
                statement = statement.where(Task.priority == priority.lower())
            
            if tags:
                tag_list = [t.strip() for t in tags.split(",")]
                # Search in tags field (comma-separated string)
                for tag in tag_list:
                    statement = statement.where(Task.tags.contains(tag))
            
            if search:
                # Search in title and description
                statement = statement.where(
                    (Task.title.contains(search)) | 
                    (Task.description.contains(search))
                )
            
            tasks = session.exec(statement).all()
            
            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": "completed" if task.completed else "pending",
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                })
            
            return {
                "status": "success",
                "message": f"Found {len(task_list)} tasks",
                "tasks": task_list,
                "filters_applied": {
                    "status": status,
                    "priority": priority,
                    "tags": tags,
                    "search": search
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list tasks: {str(e)}"
        }
```

**Update Tool Function** in `todo_tools.py`:
```python
def list_tasks_tool(
    user_id: str = "",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict]:
    """
    List all tasks for a user via tool with optional filters
    """
    result = TaskOperationsService.list_tasks(
        user_id, status, priority, tags, search
    )
    return result.get("tasks", [])
```

**Acceptance Criteria**:
- [ ] `list_tasks()` accepts optional filter parameters
- [ ] Filter by status (pending/completed)
- [ ] Filter by priority (high/medium/low)
- [ ] Filter by tags (comma-separated)
- [ ] Search in title and description
- [ ] `list_tasks_tool()` updated with same parameters
- [ ] Returns applied filters in response for transparency

---

### Task 2.3: Update LLM Tool Definitions
**File**: `phase3/backend/src/services/ai_agent.py`
**Location**: Lines ~401-470 (tools definition)

**Add New Tool Definition**:
```python
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
            "required": ["task_id"]
        }
    }
}
```

**Update `list_tasks` Tool Definition**:
```python
{
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "List tasks for the user. Can filter by status (pending/completed/all), priority (high/medium/low), tags, or search keywords.",
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
        }
    }
}
```

**Acceptance Criteria**:
- [ ] `get_task_details` tool defined with proper description
- [ ] `list_tasks` tool updated with filter parameters
- [ ] Tool descriptions guide LLM on when to use each

---

## Phase 3: System Prompt Enhancement

### Task 3.1: Update System Prompt
**File**: `phase3/backend/src/services/ai_agent.py`
**Location**: Lines ~473-525

**Add to System Prompt**:
```python
"CONTEXT AWARENESS:\n"
"- You have access to the last 10 messages in this conversation\n"
"- Reference previous messages when user says 'that task', 'the one I mentioned', etc.\n"
"- If user refers to something from earlier, use conversation history to understand\n\n"

"TASK QUERY INTELLIGENCE:\n"
"- When user asks 'what are my completed tasks?' → call list_tasks(status='completed')\n"
"- When user asks 'show pending tasks' → call list_tasks(status='pending')\n"
"- When user asks 'tell me about [task name]' → first call list_tasks(search='[task name]'), then get_task_details(task_id)\n"
"- When user asks 'high priority tasks' → call list_tasks(priority='high')\n"
"- When user asks 'tasks about [topic]' → call list_tasks(search='[topic]')\n\n"

"TASK ID RESOLUTION:\n"
"- If user says 'task 3' or 'the third task', first call list_tasks() to get the list\n"
"- Count to find the task at position 3, extract its ID, then operate on it\n"
"- Never assume task IDs are sequential numbers\n\n"

"RESPONSE FORMAT:\n"
"- Be conversational and friendly\n"
"- When showing tasks, format clearly with status indicators\n"
"- For completed tasks: ✅ Task Name\n"
"- For pending tasks: ⏳ Task Name\n"
"- Always mention due dates if they exist\n"
```

**Acceptance Criteria**:
- [ ] System prompt includes context awareness instructions
- [ ] System prompt includes specific examples for filtered queries
- [ ] System prompt guides LLM on task ID resolution
- [ ] Response format guidelines included

---

## Phase 4: Integration Testing

### Task 4.1: Test Conversation History
**Test Cases**:
```python
# Test 1: Follow-up question references previous message
User: "Show me my tasks"
AI: [shows 5 tasks]
User: "What about the third one?"
Expected: AI knows which task is "the third one" from context

# Test 2: Pronoun resolution
User: "I need to buy groceries tomorrow"
AI: [creates task]
User: "Can you mark it as high priority?"
Expected: AI knows "it" refers to the groceries task

# Test 3: Context across multiple turns
User: "What do I have to do?"
AI: [shows pending tasks]
User: "And what's already done?"
Expected: AI understands "and" connects to previous query
```

**Acceptance Criteria**:
- [ ] Follow-up questions work correctly
- [ ] Pronouns resolved from context
- [ ] Multi-turn conversations maintain coherence

---

### Task 4.2: Test New Tools
**Test Cases**:
```python
# Test get_task_details
User: "Tell me about Call Dentist"
Expected: AI calls list_tasks(search="Call Dentist"), then get_task_details()

# Test filtered list_tasks
User: "Show completed tasks"
Expected: AI calls list_tasks(status="completed")

User: "High priority stuff"
Expected: AI calls list_tasks(priority="high")

User: "Tasks about meeting"
Expected: AI calls list_tasks(search="meeting")
```

**Acceptance Criteria**:
- [ ] `get_task_details` returns full task info
- [ ] `list_tasks(status="completed")` filters correctly
- [ ] `list_tasks(priority="high")` filters correctly
- [ ] `list_tasks(search="meeting")` finds matching tasks

---

### Task 4.3: Test Edge Cases
**Test Cases**:
```python
# Test 1: Task not found
User: "Tell me about nonexistent task"
Expected: AI gracefully explains task doesn't exist

# Test 2: No conversation history
User: [first message in new conversation]
Expected: Works without errors, empty history

# Test 3: Very long conversation
User: [20+ messages in conversation]
Expected: Only last 10 messages fetched, no performance issues

# Test 4: User tries to access another user's task
User: "get_task_details(task_id=other_users_task)"
Expected: Returns "Access denied" error
```

**Acceptance Criteria**:
- [ ] All edge cases handled gracefully
- [ ] No crashes on invalid input
- [ ] User isolation enforced

---

## Phase 5: Documentation & Cleanup

### Task 5.1: Update Architecture Documentation
**File**: `PHASE3_ARCHITECTURE.md`

**Updates Needed**:
- [ ] Update architecture diagram to show conversation history flow
- [ ] Document tool definitions
- [ ] Add section on conversation context handling
- [ ] Remove references to hardcoded logic

---

### Task 5.2: Code Cleanup
**Files to Clean**:
- [ ] Remove unused imports from `ai_agent.py` (regex, keyword lists)
- [ ] Remove unused variables (`complete_keywords`, `delete_keywords`, etc.)
- [ ] Add docstrings to new methods
- [ ] Add type hints where missing

---

## Implementation Order

```
Week 1: Foundation
├── Day 1-2: Task 1.1 - Remove hardcoded logic
├── Day 3-4: Task 1.2 - Add conversation history fetching
└── Day 5: Test Phase 1 changes

Week 2: Tools
├── Day 1-2: Task 2.1 - Add get_task_details tool
├── Day 3-4: Task 2.2 - Add filtering to list_tasks
├── Day 5: Task 2.3 - Update LLM tool definitions

Week 3: Polish
├── Day 1-2: Task 3.1 - Update system prompt
├── Day 3-4: Task 4.1-4.3 - Integration testing
└── Day 5: Task 5.1-5.2 - Documentation & cleanup
```

---

## Success Metrics

| Metric | Before | After Target |
|--------|--------|--------------|
| User asks "completed tasks" → Shows completed | ❌ 0% | ✅ 100% |
| User asks "details of X" → Shows details | ❌ 0% | ✅ 100% |
| Follow-up question understands context | ❌ 0% | ✅ 90%+ |
| LLM actually interprets intent | ❌ 0% | ✅ 100% |
| Hardcoded Python logic | ✅ 315 lines | ❌ 0 lines |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM makes wrong tool calls | Add few-shot examples in system prompt |
| Conversation history too long | Limit to last 10 messages |
| Performance impact from DB queries | Add indexes on `conversation_id`, `timestamp` |
| Breaking existing functionality | Run existing tests after each phase |
| Token limit exceeded | Truncate long messages, limit history |

---

## Files to Modify

| File | Changes | Lines Affected |
|------|---------|----------------|
| `phase3/backend/src/services/ai_agent.py` | Remove hardcoded logic, add history fetch, update tools, update prompt | ~400 lines |
| `phase3/backend/src/services/mcp_server/todo_tools.py` | Add `get_task_details_tool`, update `list_tasks_tool` | +30 lines |
| `phase3/backend/src/services/task_operations.py` | Add `get_task_details()`, update `list_tasks()` | +80 lines |
| `PHASE3_ARCHITECTURE.md` | Update documentation | +50 lines |

---

## Next Steps

1. **Review and approve this plan**
2. **Create backup branch**: `git checkout -b backup-before-agent-fix`
3. **Start Phase 1**: Remove hardcoded logic
4. **Test after each phase**: Don't batch changes
5. **Deploy to staging**: Test with real users before production

---

## Appendix: Expected Behavior After Fix

### User Question Flow

```
User: "what are my completed tasks?"
│
├─▶ Chatbot Service saves message to DB
│
├─▶ AI Agent fetches last 10 messages from DB (context)
│
├─▶ AI Agent sends to LLM:
│    [system prompt]
│    [conversation history]
│    [user: "what are my completed tasks?"]
│
├─▶ LLM analyzes intent → decides to call list_tasks(status="completed")
│
├─▶ AI Agent executes list_tasks_tool(status="completed")
│
├─▶ TaskOperationsService queries DB:
│    SELECT * FROM tasks 
│    WHERE user_id = ? AND completed = true
│
├─▶ Results returned to LLM
│
├─▶ LLM generates: "You have 3 completed tasks: ✅ Task1, ✅ Task2..."
│
└─▶ Response saved to DB and returned to user
```

### Follow-up Question Flow

```
User: "tell me about Call Dentist"
│
├─▶ AI Agent fetches conversation history (includes previous exchange)
│
├─▶ LLM receives context + new question
│
├─▶ LLM calls list_tasks(search="Call Dentist")
│
├─▶ Returns task with ID: "abc-123-xyz"
│
├─▶ LLM calls get_task_details(task_id="abc-123-xyz")
│
├─▶ Returns full details: description, priority, due date, etc.
│
└─▶ LLM generates: "Call Dentist - Description: Schedule annual checkup. 
     Priority: Medium. Due: March 30, 2026."
```
