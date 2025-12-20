# Quickstart: AI-Powered Todo Chatbot with Voice Support

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- PostgreSQL database (Neon Serverless recommended)
- Better Auth configured
- Google AI API key for Gemini 2.5 Flash model
- MCP SDK installed

## Environment Setup

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart pydantic google-generativeai python-dotenv
   pip install aiomcp  # For MCP server implementation
   ```

2. **Set up environment variables**:
   ```bash
   # Create .env file in backend root
   GOOGLE_API_KEY=your_google_api_key_here
   DATABASE_URL=postgresql://your_neon_db_url
   MCP_SERVER_PORT=8001
   ```

3. **Database Migrations**:
   ```bash
   # Run the migrations to create conversation and message tables
   # This will create the tables as specified in data-model.md
   ```

### Frontend Setup

1. **Install frontend dependencies**:
   ```bash
   npm install @xenova/transformers  # For client-side voice processing (optional)
   # Or use browser's built-in Web Speech API
   ```

2. **Update environment variables**:
   ```bash
   # In frontend .env file
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_MCP_SERVER_URL=http://localhost:8001
   ```

## Running the Application

### Backend Services

1. **Start the main API server**:
   ```bash
   cd phase3/backend  # or wherever your backend is located
   uvicorn main:app --reload --port 8000
   ```

2. **Start the MCP server**:
   ```bash
   python -m mcp.server --port 8001
   # Or run your custom MCP server implementation
   ```

### Frontend

1. **Start the frontend**:
   ```bash
   cd frontend  # or wherever your Next.js app is
   npm run dev
   ```

## API Endpoints

### Chatbot Endpoints

- `POST /api/v1/chat/send` - Send message to AI chatbot
- `GET /api/v1/chat/conversations` - List user conversations
- `GET /api/v1/chat/conversations/{id}` - Get specific conversation
- `GET /api/v1/chat/conversations/{id}/messages` - Get conversation messages
- `POST /api/v1/chat/voice-recognize` - Convert voice to text (if server-side processing needed)

### Example Usage

#### Send a text message:
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Add a task to buy groceries",
    "message_type": "text"
  }'
```

#### Send a voice-converted message:
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Show me all my tasks",
    "message_type": "voice",
    "conversation_id": "existing-conversation-uuid"
  }'
```

## MCP Server Configuration

The Model Context Protocol (MCP) server exposes todo operations as tools for the AI agent:

- `create_task` - Create a new task
- `list_tasks` - List all tasks for the user
- `update_task` - Update an existing task
- `delete_task` - Delete a task
- `complete_task` - Mark a task as complete

## Voice Processing Flow

1. User clicks voice input button in UI
2. Browser Web Speech API captures audio
3. Speech is converted to text in browser
4. Text is sent to chat endpoint with message_type="voice"
5. AI agent processes the text using MCP tools
6. Response is returned to the UI

## Development

### Running Tests
```bash
# Backend tests
pytest tests/ -v

# Frontend tests
npm run test
```

### Adding New MCP Tools
To add new capabilities for the AI agent, create new MCP tool functions in the MCP server:

```python
# Example MCP tool definition
@server.tool(
    name="search_tasks",
    description="Search tasks by keyword",
    parameters={
        "keyword": {"type": "string", "description": "Keyword to search for in task titles/descriptions"}
    }
)
async def search_tasks(keyword: str) -> dict:
    # Implementation here
    pass
```