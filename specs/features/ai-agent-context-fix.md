# Feature: AI Agent with Conversation Context and LLM-First Intent Detection

## Spec Status
- **Status**: Draft
- **Created**: 2026-03-24
- **Phase**: Phase III - AI-Powered Todo Chatbot
- **Priority**: Critical (Fixes broken agent behavior)

---

## Problem Statement

### Current Issues

1. **Hardcoded Keyword Detection Bypasses LLM**
   - Lines 85-400 in `ai_agent.py` contain hardcoded Python keyword detection
   - User queries like "what are my completed tasks?" trigger `is_task_related = True`
   - Code returns ALL tasks immediately without LLM interpretation
   - User questions like "details of Call Dentist" fail because no `get_task_details` tool exists

2. **No Conversation History Passed to LLM**
   - Messages are saved to database but never fetched for context
   - Each user message is sent to LLM in isolation
   - Follow-up questions fail: "What about the third one?" has no context
   - Pronoun resolution impossible: "Mark it as done" - LLM doesn't know what "it" is

3. **Missing Tools**
   - No `get_task_details(task_id)` tool for querying specific tasks
   - `list_tasks()` has no filtering (status, priority, tags, search)
   - LLM cannot express nuanced queries

4. **Violates Hackathon Spec**
   - Spec says: "AI agents use MCP tools to manage tasks"
   - Reality: Python code intercepts and handles everything
   - Spec says: "Stateless chat endpoint with DB persistence"
   - Reality: DB persistence exists but context not used

### User Impact

| User Question | Current Behavior | Expected Behavior |
|---------------|------------------|-------------------|
| "what are my completed tasks?" | Shows ALL tasks (no filter) | Shows only completed tasks |
| "details of Call Dentist" | Shows task list again | Shows task details |
| "mark the third task done" | Fails (no context) | Resolves "third task" from history |
| "high priority stuff" | Shows ALL tasks | Shows high priority only |

---

## User Stories

1. **As a user**, I can ask "what are my completed tasks?" and see only completed tasks
2. **As a user**, I can ask "tell me about [task name]" and get detailed information
3. **As a user**, I can ask follow-up questions that reference previous messages
4. **As a user**, I can say "mark it as done" and the AI knows what "it" refers to
5. **As a user**, I can filter tasks by priority, status, or search keywords naturally
6. **As a user**, I expect the AI to understand my intent, not match keywords

---

## Acceptance Criteria

### AC1: Remove All Hardcoded Intent Detection
- [ ] Delete keyword detection code (lines 85-400 in current `ai_agent.py`)
- [ ] Delete all `is_task_related`, `is_complete_intent`, `is_delete_intent`, `is_update_intent` blocks
- [ ] Delete hardcoded response formatting for each intent type
- [ ] `process_message()` goes directly to LLM call after logging
- [ ] **Test**: Query "completed tasks" reaches LLM, not Python filter code

### AC2: Fetch and Pass Conversation History to LLM
- [ ] New method `_get_conversation_history(conversation_id, user_id, max_messages=10)`
- [ ] Fetches last 10 messages from `Message` table ordered by timestamp
- [ ] Returns list of `{role: str, content: str}` dicts
- [ ] Messages inserted between system prompt and current user message
- [ ] Returns empty list if no conversation_id or on error (graceful degradation)
- [ ] **Test**: Follow-up question "what about the third one?" resolves correctly

### AC3: Add `get_task_details` Tool
- [ ] New tool `get_task_details_tool(task_id, user_id)` in `todo_tools.py`
- [ ] New method `TaskOperationsService.get_task_details(task_id, user_id)`
- [ ] Returns full task details: id, title, description, status, priority, tags, due_date, timestamps
- [ ] Verifies user ownership before returning details
- [ ] Returns error if task not found or access denied
- [ ] Tool definition added to LLM's available tools
- [ ] **Test**: Query "tell me about Call Dentist" returns task details

### AC4: Add Filtering to `list_tasks`
- [ ] Update `list_tasks_tool()` signature with optional filters:
  - `status: Optional[str]` - "pending", "completed", "all"
  - `priority: Optional[str]` - "high", "medium", "low"
  - `tags: Optional[str]` - comma-separated tags
  - `search: Optional[str]` - keyword search in title/description
- [ ] Update `TaskOperationsService.list_tasks()` with same filters
- [ ] SQL filters applied via SQLModel `where()` clauses
- [ ] Returns applied filters in response for transparency
- [ ] Tool definition updated with filter parameters and enum constraints
- [ ] **Test**: Query "high priority tasks" returns only high priority

### AC5: Update System Prompt for Context Awareness
- [ ] Add "CONTEXT AWARENESS" section explaining history availability
- [ ] Add "TASK QUERY INTELLIGENCE" with specific examples:
  - "completed tasks" → `list_tasks(status='completed')`
  - "pending tasks" → `list_tasks(status='pending')`
  - "tell me about X" → `list_tasks(search='X')` then `get_task_details()`
  - "high priority" → `list_tasks(priority='high')`
- [ ] Add "TASK ID RESOLUTION" for handling "task 3" references
- [ ] Add response format guidelines with status indicators (✅, ⏳)
- [ ] **Test**: LLM calls correct tools for filtered queries

### AC6: Integration Tests Pass
- [ ] Test conversation flow with follow-up questions
- [ ] Test all filter combinations (status, priority, search)
- [ ] Test `get_task_details` for existing and non-existing tasks
- [ ] Test edge cases: empty history, invalid task_id, cross-user access
- [ ] Test pronoun resolution from context
- [ ] **Test**: All tests pass with 90%+ success rate

---

## Technical Specification

### Architecture Changes

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT SERVICE (FIXED)                     │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  process_message()                                        │ │
│  │  1. Log request                                           │ │
│  │  2. Fetch conversation history from DB ← NEW              │ │
│  │  3. Build messages: [system, ...history, user] ← CHANGED  │ │
│  │  4. Call LLM with tools ← NO HARDCODED INTERCEPTION       │ │
│  │  5. Execute tools called by LLM                           │ │
│  │  6. Return natural language response                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  _get_conversation_history() ← NEW METHOD                 │ │
│  │  - SELECT * FROM message WHERE conversation_id = ?        │ │
│  │  - ORDER BY timestamp DESC LIMIT 10                       │ │
│  │  - Return [{role, content}, ...]                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User: "what are my completed tasks?"
  │
  ▼
┌─────────────────────────────────────────┐
│  Chatbot Service                        │
│  - Saves message to DB                  │
│  - Calls ai_agent.process_message()     │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  AI Agent: process_message()            │
│  - Fetches last 10 messages from DB     │
│  - Builds: [system, msg1, msg2, user]   │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  LLM (Groq - Llama 3.3)                 │
│  System: "You are a helpful assistant"  │
│  + Context: Last 10 messages            │
│  + User: "what are my completed tasks?" │
│  + Tools: [list_tasks, get_task, ...]   │
│                                         │
│  LLM Decision: Call list_tasks(status="completed")
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  MCP Tool: list_tasks(status="completed")│
│  - SELECT * FROM task                   │
│  - WHERE user_id = ? AND completed=T    │
│  - Returns filtered list                │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  LLM generates response                 │
│  "You have 3 completed tasks:           │
│   ✅ Task1, ✅ Task2, ✅ Task3"         │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  Response saved to DB + returned        │
└─────────────────────────────────────────┘
```

### Database Schema (No Changes Required)

Existing tables support the feature:

```sql
-- Message table already has:
id: UUID (PK)
conversation_id: UUID (FK)
user_id: UUID (FK)
role: VARCHAR (user/assistant)
content: TEXT
message_type: VARCHAR (text/voice)
timestamp: DATETIME

-- Query for conversation history:
SELECT role, content, timestamp
FROM message
WHERE conversation_id = ?
ORDER BY timestamp DESC
LIMIT 10
```

### API Changes

#### New Tool: `get_task_details`

**Location**: `phase3/backend/src/services/mcp_server/todo_tools.py`

```python
def get_task_details_tool(task_id: str, user_id: str = "") -> Dict:
    """
    Get detailed information about a specific task by ID.
    
    Parameters:
    - task_id: UUID of the task
    - user_id: User's UUID for ownership verification
    
    Returns:
    - Dict with status, task details, or error message
    """
    return TaskOperationsService.get_task_details(task_id, user_id)
```

#### Updated Tool: `list_tasks` with Filters

**Location**: `phase3/backend/src/services/mcp_server/todo_tools.py`

```python
def list_tasks_tool(
    user_id: str = "",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict]:
    """
    List tasks for user with optional filters.
    
    Parameters:
    - user_id: User's UUID
    - status: "pending", "completed", or "all"
    - priority: "high", "medium", or "low"
    - tags: Comma-separated tags
    - search: Keyword search in title/description
    
    Returns:
    - List of task dicts matching filters
    """
    result = TaskOperationsService.list_tasks(
        user_id, status, priority, tags, search
    )
    return result.get("tasks", [])
```

### Code Changes Summary

| File | Changes | Lines Added | Lines Removed |
|------|---------|-------------|---------------|
| `ai_agent.py` | Remove hardcoded logic, add history fetch, update prompt | +100 | -315 |
| `ai_agent.py` | Add `_get_conversation_history()` method | +35 | 0 |
| `todo_tools.py` | Add `get_task_details_tool()` | +15 | 0 |
| `todo_tools.py` | Update `list_tasks_tool()` signature | +10 | -2 |
| `task_operations.py` | Add `get_task_details()` method | +40 | 0 |
| `task_operations.py` | Update `list_tasks()` with filters | +50 | -10 |
| **Total** | | **+250** | **-327** |

---

## Test Plan

### Test Case 1: Completed Tasks Filter
```python
# Given: User has 5 tasks (3 completed, 2 pending)
# When: User asks "what are my completed tasks?"
# Then: AI calls list_tasks(status="completed")
# And: Returns only 3 completed tasks
# And: Response includes ✅ indicators
```

### Test Case 2: Task Details Query
```python
# Given: User has task "Call Dentist"
# When: User asks "tell me about Call Dentist"
# Then: AI calls list_tasks(search="Call Dentist")
# And: AI extracts task_id and calls get_task_details(task_id)
# And: Returns title, description, priority, due date
```

### Test Case 3: Follow-up with Context
```python
# Given: Conversation history shows 5 tasks listed
# When: User asks "what about the third one?"
# Then: AI fetches conversation history (10 messages)
# And: LLM receives context including the task list
# And: LLM resolves "third one" to specific task
# And: AI calls get_task_details() for that task
```

### Test Case 4: Pronoun Resolution
```python
# Given: User says "I need to buy groceries tomorrow"
# And: AI creates task "Buy groceries"
# When: User says "mark it as high priority"
# Then: AI fetches conversation history
# And: LLM resolves "it" to "Buy groceries" task
# And: AI calls update_task(task_id, priority="high")
```

### Test Case 5: Priority Filter
```python
# Given: User has tasks with various priorities
# When: User asks "high priority stuff"
# Then: AI calls list_tasks(priority="high")
# And: Returns only high priority tasks
```

### Test Case 6: Search Filter
```python
# Given: User has tasks about meetings, calls, shopping
# When: User asks "tasks about meeting"
# Then: AI calls list_tasks(search="meeting")
# And: Returns tasks with "meeting" in title or description
```

### Test Case 7: Edge Case - No History
```python
# Given: New conversation (no history)
# When: User asks first question
# Then: _get_conversation_history() returns []
# And: LLM receives only system prompt + user message
# And: No errors occur
```

### Test Case 8: Edge Case - Task Not Found
```python
# Given: Invalid task_id
# When: User asks for details of non-existent task
# Then: get_task_details() returns error status
# And: AI responds gracefully "Task not found"
```

### Test Case 9: Edge Case - Cross-User Access
```python
# Given: Task belongs to User A
# When: User B asks for details of that task
# Then: get_task_details() verifies ownership
# And: Returns "Access denied" error
```

---

## Performance Considerations

### Database Query Optimization

```sql
-- Index for conversation history fetch
CREATE INDEX IF NOT EXISTS idx_message_conversation_timestamp 
ON message(conversation_id, timestamp DESC);

-- Index for task filtering
CREATE INDEX IF NOT EXISTS idx_task_user_completed 
ON task(user_id, completed);

CREATE INDEX IF NOT EXISTS idx_task_user_priority 
ON task(user_id, priority);
```

### Token Budget

| Component | Tokens (approx) |
|-----------|-----------------|
| System prompt | 600 |
| Conversation history (10 msgs × 50 tokens) | 500 |
| User message | 50 |
| Tool definitions (6 tools) | 400 |
| **Total input** | **~1550** |
| Max output tokens | 500 |
| **Total budget** | **~2050** |

Well within Llama 3.3's 128K context window.

---

## Migration Plan

### Phase 1: Foundation (Day 1-2)
1. Create spec and get approval
2. Backup current `ai_agent.py`
3. Remove hardcoded keyword detection (lines 85-400)
4. Add `_get_conversation_history()` method
5. Update `process_message()` to fetch and use history
6. Run basic tests

### Phase 2: Tools (Day 3-4)
1. Add `get_task_details()` to `task_operations.py`
2. Add `get_task_details_tool()` to `todo_tools.py`
3. Add filters to `list_tasks()` and `list_tasks_tool()`
4. Update LLM tool definitions in `ai_agent.py`
5. Run tool-specific tests

### Phase 3: Polish (Day 5)
1. Update system prompt with context awareness
2. Add response formatting guidelines
3. Run integration tests
4. Update architecture documentation
5. Deploy to staging

### Rollback Plan
If issues occur:
```bash
# Revert ai_agent.py
git checkout HEAD -- phase3/backend/src/services/ai_agent.py

# Revert todo_tools.py
git checkout HEAD -- phase3/backend/src/services/mcp_server/todo_tools.py

# Revert task_operations.py
git checkout HEAD -- phase3/backend/src/services/task_operations.py

# Restart backend
docker-compose restart backend
```

---

## Success Metrics

| Metric | Before | Target | Measurement |
|--------|--------|--------|-------------|
| "completed tasks" shows completed | 0% | 100% | Manual testing |
| "details of X" shows details | 0% | 100% | Manual testing |
| Follow-up questions work | 0% | 90%+ | Integration tests |
| LLM interprets intent | 0% | 100% | Code audit |
| Hardcoded Python logic | 315 lines | 0 lines | Line count |
| Average response time | <500ms | <800ms | Performance monitoring |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM makes wrong tool calls | Medium | High | Add few-shot examples in system prompt |
| Conversation history too long | Low | Medium | Limit to 10 messages, truncate long content |
| Database query slow | Low | Medium | Add indexes on conversation_id, timestamp |
| Breaking existing functionality | Medium | High | Run existing tests after each phase |
| Token limit exceeded | Low | Medium | Monitor token usage, adjust limits |
| API key rate limits | Medium | Medium | Implement retry with exponential backoff |

---

## Dependencies

### Required Environment Variables
```bash
# LLM Providers
GROQ_API_KEY=your_groq_key
BONSAI_API_KEY=your_bonsai_key

# Database (already configured)
DATABASE_URL=postgresql://...
```

### Python Dependencies (Already Installed)
```
openai>=1.0.0
sqlmodel>=0.0.14
```

---

## References

- Hackathon Spec: `hackathon-project-details.md` - Phase III requirements
- Architecture: `PHASE3_ARCHITECTURE.md` - Current architecture docs
- Original Issue: User conversation showing repeated task list responses
- Related: `AGENT_FIX_PLAN.md` - Initial analysis document

---

## Appendix: Example Conversations

### Example 1: Filtered Task Query
```
User: "what are my completed tasks?"
AI: [Calls list_tasks(status="completed")]
AI: "You have 3 completed tasks:
     ✅ Buy groceries (Due: 2026-03-20)
     ✅ Call dentist
     ✅ Finish report"
```

### Example 2: Task Details with Context
```
User: "tell me about Call Dentist"
AI: [Calls list_tasks(search="Call Dentist")]
AI: [Finds task_id: abc-123]
AI: [Calls get_task_details(task_id="abc-123")]
AI: "📋 **Call Dentist**
     
     Schedule annual dental checkup
     
     Priority: Medium
     Due: 2026-03-30
     Status: pending"
```

### Example 3: Follow-up with Pronoun Resolution
```
User: "I need to buy groceries tomorrow"
AI: [Creates task "Buy groceries" with due_date=2026-03-25]
AI: "✅ Task 'Buy groceries' created for tomorrow!"

User: "mark it as high priority"
AI: [Fetches conversation history]
AI: [LLM resolves "it" = "Buy groceries" task]
AI: [Calls update_task(task_id, priority="high")]
AI: "✏️ Updated 'Buy groceries' to high priority"
```

### Example 4: Multi-turn Task Management
```
User: "show my tasks"
AI: [Calls list_tasks(status="pending")]
AI: [Shows 5 pending tasks]

User: "what about completed ones?"
AI: [Fetches history, understands follow-up]
AI: [Calls list_tasks(status="completed")]
AI: "You have 3 completed tasks: ✅ ..."

User: "delete the second completed task"
AI: [Resolves from completed list]
AI: [Calls delete_task(task_id)]
AI: "🗑️ Deleted 'Old meeting'"
```
