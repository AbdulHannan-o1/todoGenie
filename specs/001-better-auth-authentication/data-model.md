# Data Model: Better Auth Authentication

## Entities

### User

Represents an individual with credentials to access the system.

**Attributes**:
- `id`: Unique identifier (e.g., UUID)
- `email`: Email address (unique, string)
- `username`: Username (unique, string)
- `password_hash`: Hashed password (string)
- `status`: Account status (enum: `Active`, `Suspended`, `Deleted`)

**Relationships**:
- One-to-many with `Task` (a User can own multiple Tasks)

### Task

Represents a to-do item created by a user.

**Attributes**:
- `id`: Unique identifier (e.g., UUID)
- `content`: Description of the task (string)
- `user_id`: Foreign key referencing the `User` who owns this task

**Relationships**:
- Many-to-one with `User` (a Task belongs to one User)
