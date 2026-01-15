# Phase 3 - AI Chatbot with Voice Support

## Architecture Documentation

This document describes the complete architecture of the AI-powered Todo Chatbot with voice support, explaining how Better Auth, MCP Server, and AI Agent work together.

---

## Phase 3 Requirements vs Implementation Status

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Conversational interface for all Basic Level features | ✅ Done | `chat/page.tsx`, `chatbot.py` |
| OpenAI Agents SDK for AI logic | ✅ Done | `ai_agent.py` - Using OpenAI-compatible API |
| MCP Server with Official MCP SDK | ✅ Done | `mcp_server/todo_tools.py`, `mcp_server/mcp_server.py` |
| Stateless chat endpoint with DB persistence | ✅ Done | `chat/send` endpoint + `Conversation`, `Message` models |
| AI agents use MCP tools to manage tasks | ✅ Done | `create_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task` |
| Conversation history persistence | ✅ Done | `conversation_service.py`, `models/conversation.py` |
| Voice input support | ✅ Done | `voice_processor.py`, `VoiceInput.tsx` |
| JWT Authentication with Better Auth | ✅ Done | `auth.py`, `api/dependencies.py` |

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER INTERFACE                                     │
│  ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐   │
│  │   Dashboard Page    │     │    Chat Page        │     │   Login Page        │   │
│  │   (Task List)       │     │   (AI Chatbot)      │     │   (Auth)            │   │
│  └──────────┬──────────┘     └──────────┬──────────┘     └──────────┬──────────┘   │
│             │                           │                           │              │
│             └───────────────────────────┼───────────────────────────┘              │
│                                         │                                          │
└────────────────────────────┐            │            ┌─────────────────────────────┘
                             │            │            │
                             ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              NEXT.JS FRONTEND (Port 3000)                            │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         Better Auth (Client-side)                            │   │
│  │  ┌────────────────┐    ┌────────────────┐    ┌────────────────────────┐    │   │
│  │  │ Sign Up/Login  │───▶│  JWT Token     │───▶│  Auth Context          │    │   │
│  │  │  Component     │     │  Generation    │     │  (useAuth hook)       │    │   │
│  │  └────────────────┘     └────────────────┘     └────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐            │
│  │  API Client (lib/api.ts)     │    │  Voice Processor             │            │
│  │  - Attaches JWT to headers   │    │  - Speech to Text            │            │
│  │  - Handles all REST calls    │    │  - Text to Speech            │            │
│  └──────────────────────────────┘    └──────────────────────────────┘            │
│                                                                                      │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐            │
│  │  Chat Component              │    │  Task Components             │            │
│  │  - Message display           │    │  - Task cards, forms         │            │
│  │  - Input field               │    │  - Filters, search           │            │
│  │  - Auto-scroll               │    │  - Priority, tags UI         │            │
│  └──────────────────────────────┘    └──────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                      POST /api/v1/chat/send
                      GET  /api/v1/chat/conversations
                      JWT Token in Authorization Header
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND (Port 8000)                               │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         Authentication Layer                                 │   │
│  │  ┌────────────────────────┐    ┌────────────────────────────────────────┐  │   │
│  │  │  JWT Verification      │    │  get_current_active_user Dependency   │  │   │
│  │  │  (Better Auth Secret)  │───▶│  - Validates JWT token                │  │   │
│  │  │                        │    │  - Extracts user_id                   │  │   │
│  │  └────────────────────────┘    │  - Returns User or 401                │  │   │
│  │                                  └────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         API Endpoints                                        │   │
│  │                                                                              │   │
│  │  POST /api/v1/chat/send           GET /api/v1/chat/conversations            │   │
│  │  GET  /api/v1/chat/conversations/{id}   DELETE /api/v1/chat/conversations   │   │
│  │  POST /api/v1/voice/transcribe    GET /api/v1/tasks                         │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                    ┌────────────────────┼────────────────────┐                     │
│                    ▼                    ▼                    ▼                     │
│  ┌──────────────────┐   ┌──────────────────────┐   ┌────────────────────────┐    │
│  │ Chatbot Service  │   │  Task Service        │   │  Conversation Service  │    │
│  │ (Orchestrator)   │   │  (CRUD Operations)   │   │  (History Management)  │    │
│  └────────┬─────────┘   └──────────────────────┘   └────────────────────────┘    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐     │
│  │                     AI AGENT SERVICE (Agentic Loop)                     │     │
│  │                                                                        │     │
│  │   ┌─────────────────────────────────────────────────────────────────┐  │     │
│  │   │  OpenAI-Compatible Client (Groq API - Llama 3.3)                │  │     │
│  │   │  - Sends messages with tool definitions                         │  │     │
│  │   │  - Receives tool calls or text responses                        │  │     │
│  │   └─────────────────────────────┬───────────────────────────────────┘  │     │
│  │                                 │                                      │     │
│  │   ┌─────────────────────────────▼───────────────────────────────────┐  │     │
│  │   │  Agentic Loop (Up to 5 iterations)                              │  │     │
│  │   │                                                                  │  │     │
│  │   │  1. User sends message                                          │  │     │
│  │   │  2. AI analyzes intent                                          │  │     │
│  │   │  3. AI calls list_tasks() if needed                             │  │     │
│  │   │  4. AI sees results, calls complete_task(task_id)               │  │     │
│  │   │  5. Loop continues until no more tool calls                     │  │     │
│  │   │  6. Final response sent to user                                 │  │     │
│  │   │                                                                  │  │     │
│  │   └──────────────────────────────────────────────────────────────────┘  │     │
│  └───────────────────────────────────────────────────────────────────────────┘     │
│                                         │                                          │
└─────────────────────────────────────────┼──────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          MCP SERVER (Model Context Protocol)                         │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         MCP Tools (Exposed to AI)                           │   │
│  │                                                                              │   │
│  │  create_task(title, description, tags, priority, due_date, user_id)        │   │
│  │  ───────────────────────────────────────────────────────────────           │   │
│  │  list_tasks(user_id)                                                        │   │
│  │  ───────────────────────────────────────────────────────────────           │   │
│  │  complete_task(task_id, completed, user_id)                                │   │
│  │  ───────────────────────────────────────────────────────────────           │   │
│  │  update_task(task_id, title, description, status, priority, due_date)     │   │
│  │  ───────────────────────────────────────────────────────────────           │   │
│  │  delete_task(task_id, user_id)                                             │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                    ┌────────────────────┼────────────────────┐                     │
│                    ▼                    ▼                    ▼                     │
│          ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│          │ TaskOperations  │   │ TaskOperations  │   │ TaskOperations  │          │
│          │   Service       │   │   Service       │   │   Service       │          │
│          │  (Create)       │   │   (Read)        │   │  (Update)       │          │
│          └─────────────────┘   └─────────────────┘   └─────────────────┘          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              NEON POSTGRES DATABASE                                  │
│                                                                                      │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────────────┐    │
│  │      users        │   │      tasks        │   │      conversations        │    │
│  │  ─────────────    │   │  ─────────────    │   │  ─────────────────────    │    │
│  │  id (UUID)        │   │  id (UUID)        │   │  id (UUID)                │    │
│  │  email            │   │  user_id (FK)     │   │  user_id (FK)             │    │
│  │  username         │   │  title            │   │  title                    │    │
│  │  hashed_password  │   │  description      │   │  created_at               │    │
│  │  status           │   │  status           │   │  updated_at               │    │
│  │  created_at       │   │  priority         │   └───────────────────────────┘    │
│  │                   │   │  tags             │                                     │
│  │                   │   │  due_date         │   ┌───────────────────────────┐    │
│  │                   │   │  recurrence       │   │      messages             │    │
│  │                   │   │  completed        │   │  ─────────────────────    │    │
│  │                   │   │  created_at       │   │  id (UUID)                │    │
│  │                   │   │  updated_at       │   │  conversation_id (FK)     │    │
│  │                   │   └───────────────────┘   │  user_id (FK)             │    │
│  │                   │                           │  role (user/assistant)     │    │
│  │                   │                           │  content                  │    │
│  └───────────────────┘                           │  message_type             │    │
│                                                   │  created_at               │    │
│                                                   └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Cycle: User Login to Task Completion

### Step 1: User Authentication (Login)

```
User enters email/password
        │
        ▼
┌───────────────────┐
│  Better Auth      │  ◀── Frontend
│  (Client-side)    │
└────────┬──────────┘
         │
         │ Creates JWT Token
         │ (expires in 7 days)
         ▼
┌───────────────────┐     ┌───────────────────────────┐
│  JWT Token        │────▶│  Stored in localStorage   │
│  (Contains:       │     │  (Authorization: Bearer)  │
│   - user_id       │     └───────────────────────────┘
│   - email         │
│   - expiry)       │
└───────────────────┘
```

### Step 2: Frontend Makes Authenticated Request

```
User: "Create a task to buy groceries tomorrow"
        │
        ▼
┌─────────────────────────────────────────┐
│  API Request                            │
│  POST /api/v1/chat/send                 │
│  Headers:                               │
│  - Authorization: Bearer <JWT_TOKEN>    │
│  - Content-Type: application/json       │
│  Body:                                  │
│  {                                      │
│    "content": "Create a task to buy...",│
│    "message_type": "text",              │
│    "conversation_id": null              │
│  }                                      │
└────────────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend                        │
│  (middleware validates JWT)             │
└────────────────────────┬────────────────┘
                         │
                         │ JWT Verification
                         ▼
┌─────────────────────────────────────────┐
│  get_current_active_user Dependency     │
│  ───────────────────────────────────    │
│  1. Extract token from header           │
│  2. Verify signature using BETTER_AUTH_ │
│     SECRET                              │
│  3. Decode payload to get user_id       │
│  4. Query database for user             │
│  5. Return User object or 401           │
└────────────────────────┬────────────────┘
                         │
                         │ Valid user
                         ▼
┌─────────────────────────────────────────┐
│  ChatbotService.process_user_message()  │
└────────────────────────┬────────────────┘
```

### Step 3: Message Processing & Conversation Management

```
process_user_message(user_id, content, conversation_id)
        │
        ├─▶ Get or Create Conversation
        │       │
        │       ▼
        │   ┌─────────────────────────┐
        │   │ Conversation Service    │
        │   │ - Check if conv exists  │
        │   │ - If not, create new    │
        │   │ - Return conversation   │
        │   └─────────────────────────┘
        │
        ├─▶ Save User Message
        │       │
        │       ▼
        │   ┌─────────────────────────┐
        │   │ Message Model           │
        │   │ - role: "user"          │
        │   │ - content: "Create a..."│
        │   │ - conversation_id: UUID │
        │   └─────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  AI Agent Service.process_message()     │
│  (Agentic Loop Begins)                  │
└────────────────────────┬────────────────┘
```

### Step 4: AI Agent Processing (Agentic Loop)

```
AI Agent receives: "Create a task to buy groceries tomorrow"
        │
        ▼
┌─────────────────────────────────────────┐
│  System Prompt                          │
│  ───────────────                        │
│  "You are a task management AI..."      │
│  "When user wants to create a task,     │
│   call create_task with title,          │
│   description, tags, priority, due_date"│
└────────────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│  OpenAI API Call (Groq - Llama 3.3)     │
│  Messages:                              │
│  [                                     │
│    {role: "system", content: "..."},    │
│    {role: "user", content: "Create..."} │
│  ]                                      │
│  Tools: [create_task, list_tasks,       │
│         complete_task, update_task,      │
│         delete_task]                    │
└────────────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│  Model Response                         │
│  ──────────────                         │
│  Tool Calls:                            │
│  [                                     │
│    {                                    │
│      function: {                        │
│        name: "create_task",             │
│        arguments: {                     │
│          "title": "Buy groceries",      │
│          "description": "",             │
│          "tags": "",                    │
│          "priority": "medium",          │
│          "due_date": "2025-01-06"      │
│        }                                │
│      }                                  │
│    }                                    │
│  ]                                      │
│  Finish Reason: "tool_calls"            │
└────────────────────────┬────────────────┘
                         │
                         │ Tool call detected
                         ▼
┌─────────────────────────────────────────┐
│  Execute Tool (MCP)                     │
│  ────────────────                       │
│  create_task_tool(                      │
│    title="Buy groceries",               │
│    description="",                      │
│    tags="",                             │
│    priority="medium",                   │
│    due_date="2025-01-06",              │
│    user_id="uuid-from-jwt"              │
│  )                                      │
└────────────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│  TaskOperationsService.create_task()    │
│  ───────────────────────────────────    │
│  1. Validate user_id (UUID)             │
│  2. Create Task object                  │
│  3. Save to database                    │
│  4. Return result:                      │
│  {                                      │
│    "status": "success",                 │
│    "message": "Task created",           │
│    "task_id": "uuid",                   │
│    "task": {title, description, ...}    │
│  }                                      │
└────────────────────────┬────────────────┘
                         │
                         │ Tool result
                         ▼
┌─────────────────────────────────────────┐
│  Add Tool Result to Messages            │
│  ────────────────────────────           │
│  [                                     │
│    {role: "tool", content: "{result}"},│
│    tool_call_id: "call_123"            │
│  ]                                      │
└────────────────────────┬────────────────┘
                         │
                         │ Loop continues (max 5 iterations)
                         ▼
┌─────────────────────────────────────────┐
│  Final AI Response                      │
│  ─────────────────                      │
│  "Task 'Buy groceries' created!         │
│   Due: January 6, 2025                  │
│   Priority: Medium"                     │
└────────────────────────┬────────────────┘
```

### Step 5: Save Response & Return to User

```
Final AI response: "Task 'Buy groceries' created!"
        │
        ├─▶ Save Assistant Message
        │       │
        │       ▼
        │   ┌─────────────────────────┐
        │   │ Message Model           │
        │   │ - role: "assistant"     │
        │   │ - content: "Task 'Buy..."│
        │   └─────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Return to Frontend                     │
│  ─────────────────────                  │
│  {                                      │
│    "conversation_id": "uuid",           │
│    "response": "Task 'Buy groceries'...",│
│    "tool_results": [{"status": "..."}]  │
│  }                                      │
└────────────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│  Frontend Updates UI                    │
│  ───────────────────                    │
│  - Add bot message to chat              │
│  - Scroll to bottom                     │
│  - Update conversation list             │
│  - Show toast notification              │
└─────────────────────────────────────────┘
```

---

## Data Flow Summary

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                    USER                                           │
│                              "Create task"                                        │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                                   │
│  1. Add JWT token to Authorization header                                        │
│  2. Send POST /api/v1/chat/send                                                   │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                                    │
│  1. Validate JWT token (get_current_active_user)                                 │
│  2. Extract user_id from token                                                   │
│  3. Get/create conversation                                                      │
│  4. Save user message to DB                                                      │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            AI AGENT (Groq + Llama 3.3)                           │
│  1. Send user message + system prompt to LLM                                     │
│  2. LLM returns tool call (create_task)                                          │
│  3. Execute MCP tool → TaskOperationsService                                     │
│  4. Return result to LLM                                                         │
│  5. LLM generates final response                                                 │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            DATABASE (Neon PostgreSQL)                             │
│  1. Store conversation + messages                                                │
│  2. Create task record                                                           │
│  3. Return task_id to agent                                                      │
└──────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND RESPONSE                                     │
│  {conversation_id, response, tool_results}                                       │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND DISPLAY                                     │
│  Show bot response in chat window                                                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Better Auth + JWT Authentication
- **Frontend**: Better Auth creates JWT tokens on login
- **Backend**: JWT verification using `BETTER_AUTH_SECRET`
- **Security**: User ID extracted from token for all operations

### 2. MCP Server (Model Context Protocol)
- Exposes 5 tools: `create_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task`
- Tools map to `TaskOperationsService` methods
- Stateless - all state stored in database

### 3. AI Agent (Agentic Loop)
- **Model**: Groq's Llama 3.3 70B Versatile (OpenAI-compatible API)
- **Loop**: Up to 5 iterations for complex operations
- **Pattern**: List tasks → Analyze → Execute action → Generate response

### 4. Conversation Persistence
- **Stateless Server**: All conversation state in database
- **Messages**: Stored with role (user/assistant), content, timestamp
- **Resume**: Server can restart, conversations persist

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/send` | Send message to AI chatbot |
| GET | `/api/v1/chat/conversations` | Get all user conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation history |
| DELETE | `/api/v1/chat/conversations/{id}` | Delete conversation |
| POST | `/api/v1/voice/transcribe` | Convert voice to text |

---

## Implementation Files

### Backend
- `src/api/v1/chat.py` - Chat API endpoints
- `src/services/chatbot.py` - Chatbot orchestration
- `src/services/ai_agent.py` - AI agent with agentic loop
- `src/services/mcp_server/todo_tools.py` - MCP tool implementations
- `src/services/task_operations.py` - Task CRUD operations
- `src/api/dependencies.py` - JWT authentication
- `src/models/conversation.py` - Conversation & Message models

### Frontend
- `src/app/chat/page.tsx` - Chat interface with conversation auto-load
- `src/components/Chat/VoiceInput.tsx` - Voice input component
- `src/context/auth-context.tsx` - Authentication context
- `src/lib/api.ts` - API client with JWT handling

---

## Status Summary

✅ **Phase 3 Requirements Met:**
- [x] Conversational interface for all CRUD operations
- [x] AI Agent with OpenAI-compatible API (Groq)
- [x] MCP Server with 5 task management tools
- [x] Stateless chat with database persistence
- [x] JWT Authentication with Better Auth
- [x] Voice input support
- [x] Conversation history management
- [x] Agentic loop for multi-step operations

The implementation follows the architecture specified in the hackathon document and successfully integrates Better Auth, MCP Server, and AI Agent for a complete AI-powered todo management experience.
