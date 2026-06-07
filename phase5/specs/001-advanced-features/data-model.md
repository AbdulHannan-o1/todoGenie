# Data Model: Advanced Features for TodoGenie

## Overview
This document defines the data models required for implementing the advanced features in Phase 5 of the TodoGenie project, including recurring tasks, due date reminders, tags/categories, and event-driven architecture.

## Entity Relationships

### Task Entity (Enhanced)
The Task entity is extended to support advanced features:

```
Task
├── id: UUID
├── user_id: UUID (foreign key to User)
├── title: String (required, max 200 characters)
├── description: Text (optional, max 1000 characters)
├── completed: Boolean (default: false)
├── created_at: DateTime
├── updated_at: DateTime
├── due_date: DateTime (nullable)
├── reminder_time: DateTime (nullable)
├── recurrence_pattern: JSON (nullable)
│   ├── frequency: Enum (daily, weekly, monthly, yearly, custom)
│   ├── interval: Integer (default: 1)
│   ├── end_condition: Object
│   │   ├── type: Enum (after_occurrences, on_date, never)
│   │   ├── value: Mixed (count or date depending on type)
│   └── exceptions: Array (dates to skip)
├── tags: Array of Strings
└── priority: Enum (low, medium, high, urgent)
```

### Tag Entity
New entity to support task categorization:

```
Tag
├── id: UUID
├── user_id: UUID (foreign key to User)
├── name: String (required, unique per user)
├── color: String (optional, hex color code)
├── created_at: DateTime
└── updated_at: DateTime
```

### TaskTag Association
Junction table for many-to-many relationship between tasks and tags:

```
TaskTag
├── task_id: UUID (foreign key to Task)
└── tag_id: UUID (foreign key to Tag)
```

### Event Entity
Entity for storing task-related events:

```
Event
├── id: UUID
├── user_id: UUID (foreign key to User)
├── task_id: UUID (foreign key to Task)
├── event_type: Enum (created, updated, completed, deleted, reminder_sent)
├── event_data: JSON (payload specific to event type)
├── created_at: DateTime
└── processed: Boolean (default: false)
```

### Conversation Entity (Enhanced)
Enhanced to support advanced features in the AI chatbot:

```
Conversation
├── id: UUID
├── user_id: UUID (foreign key to User)
├── title: String (derived from first message or user-defined)
├── created_at: DateTime
└── updated_at: DateTime
```

### Message Entity (Enhanced)
Enhanced to support advanced features in the AI chatbot:

```
Message
├── id: UUID
├── user_id: UUID (foreign key to User)
├── conversation_id: UUID (foreign key to Conversation)
├── role: Enum (user, assistant)
├── content: Text
├── metadata: JSON (includes task operation details if applicable)
├── created_at: DateTime
└── processed: Boolean (default: false)
```

### Notification Entity
New entity to track scheduled notifications:

```
Notification
├── id: UUID
├── user_id: UUID (foreign key to User)
├── task_id: UUID (foreign key to Task, nullable)
├── type: Enum (reminder, recurring_task_created, system_alert)
├── message: String
├── scheduled_time: DateTime
├── sent_time: DateTime (nullable)
├── status: Enum (scheduled, sent, failed, cancelled)
└── created_at: DateTime
```

## Database Schema

### Tables

#### tasks (Enhanced)
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP WITH TIME ZONE,
    reminder_time TIMESTAMP WITH TIME ZONE,
    recurrence_pattern JSONB,
    priority VARCHAR(20) DEFAULT 'medium',
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_due_date (due_date),
    INDEX idx_tasks_completed (completed)
);
```

#### tags
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7), -- hex color code
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name),
    INDEX idx_tags_user_id (user_id)
);
```

#### task_tags
```sql
CREATE TABLE task_tags (
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

#### events
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    INDEX idx_events_user_id (user_id),
    INDEX idx_events_task_id (task_id),
    INDEX idx_events_processed (processed)
);
```

#### notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Kafka Event Schema

### Task Events
```json
{
  "event_id": "uuid",
  "event_type": "task.created|task.updated|task.completed|task.deleted",
  "user_id": "uuid",
  "task_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "due_date": "ISO 8601 datetime",
    "reminder_time": "ISO 8601 datetime",
    "recurrence_pattern": "object",
    "priority": "string",
    "tags": ["string"]
  }
}
```

### Reminder Events
```json
{
  "event_id": "uuid",
  "event_type": "reminder.scheduled|reminder.sent|reminder.failed",
  "user_id": "uuid",
  "task_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "task_title": "string",
    "due_at": "ISO 8601 datetime",
    "remind_at": "ISO 8601 datetime"
  }
}
```

### Recurring Task Events
```json
{
  "event_id": "uuid",
  "event_type": "recurring_task.generated",
  "user_id": "uuid",
  "original_task_id": "uuid",
  "new_task_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "original_task_title": "string",
    "new_task_title": "string",
    "recurrence_pattern": "object"
  }
}
```

## Indexing Strategy

### Primary Indices
- User isolation: `idx_tasks_user_id`, `idx_tags_user_id`, `idx_events_user_id`
- Query performance: `idx_tasks_due_date`, `idx_tasks_completed`
- Processing: `idx_events_processed`

### Composite Indices
- For filtered queries: `(user_id, completed)`, `(user_id, due_date)`
- For tag-based queries: `(user_id, tag_id)` in task_tags table

## Constraints and Validation

### Business Rules
1. **User Isolation**: All data is isolated by user_id
2. **Recurrence Integrity**: Recurring tasks must have valid recurrence patterns
3. **Due Date Validation**: Reminder time must be before due date
4. **Tag Uniqueness**: Tag names must be unique per user
5. **Event Consistency**: Events must reference valid users and tasks

### Referential Integrity
- Foreign key constraints ensure data consistency
- Cascade deletion for related entities (e.g., deleting a task removes related events)
- Prevent orphaned records

## Migration Considerations

### From Previous Schema
- Add new columns to existing tasks table (due_date, reminder_time, recurrence_pattern, priority)
- Create new tables (tags, task_tags, events, notifications)
- Update indexes to support new query patterns
- Migrate existing data to maintain user continuity