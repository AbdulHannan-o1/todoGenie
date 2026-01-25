# Data Model: AI-Powered Todo Chatbot with Voice Support

## Database Schema Changes

### New Tables

#### conversations
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_accounts(id), -- Using existing Better Auth user table
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB -- Additional conversation metadata if needed
);
```

#### messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_id UUID NOT NULL REFERENCES user_accounts(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')), -- User or AI assistant
    content TEXT NOT NULL, -- The actual message content (text from voice or direct input)
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'voice')), -- How the message was input
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB -- Additional message metadata (e.g., voice processing info)
);
```

### Updated Tables (if needed)

#### tasks (existing table to be extended with AI integration)
```sql
-- The existing tasks table will have new fields to support AI integration
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS ai_context JSONB; -- Store context about how the task was created via AI
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS conversation_id UUID REFERENCES conversations(id); -- Link tasks to conversations if created via AI
```

## Entity Relationships

### Conversation
- **Purpose**: Represents a single conversation thread between user and AI assistant
- **Fields**:
  - `id`: Unique identifier for the conversation
  - `user_id`: Reference to the user who owns the conversation
  - `title`: Optional title for the conversation (auto-generated from first message or user-provided)
  - `created_at`: Timestamp when conversation was started
  - `updated_at`: Timestamp when conversation was last updated
  - `metadata`: Additional data about the conversation (settings, preferences, etc.)

### Message
- **Purpose**: Represents a single message in a conversation
- **Fields**:
  - `id`: Unique identifier for the message
  - `conversation_id`: Reference to the parent conversation
  - `user_id`: Reference to the user who sent the message
  - `role`: Whether the message is from 'user' or 'assistant'
  - `content`: The actual text content of the message
  - `message_type`: Whether the original input was 'text' or 'voice'
  - `created_at`: Timestamp when the message was created
  - `metadata`: Additional data (e.g., confidence score for voice recognition, processing time)

### Task (Extended)
- **Purpose**: Represents a todo item with AI integration
- **Additional Fields**:
  - `ai_generated`: Whether the task was created via AI command
  - `ai_context`: Context about how the task was created (e.g., original voice command)
  - `conversation_id`: Reference to the conversation where the task was created

## Indexes for Performance

```sql
-- Index for efficient conversation retrieval by user
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Index for efficient message retrieval by conversation
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Index for task retrieval with AI context
CREATE INDEX idx_tasks_ai_generated ON tasks(ai_generated);
CREATE INDEX idx_tasks_conversation_id ON tasks(conversation_id);
```

## Validation Rules

### Conversation
- Must have a valid user_id that exists in user_accounts table
- Updated_at must be >= created_at
- Title (if provided) must be between 1-255 characters

### Message
- Must have a valid conversation_id that exists in conversations table
- Must have a valid user_id that exists in user_accounts table
- Role must be either 'user' or 'assistant'
- Content must not be empty
- Message_type must be either 'text' or 'voice'
- Created timestamp must be valid

### Task (AI Integration)
- If conversation_id is set, it must reference a valid conversation
- If ai_generated is true, ai_context should contain relevant information