# Data Model: Task Management

## Entities

### Task

**Description**: Represents a single unit of work or an item on a user's todo list.

**Attributes**:

*   **`id`**:
    *   **Type**: Integer
    *   **Constraints**: Primary Key, Unique
    *   **Description**: Unique identifier for the task.
*   **`user_id`**:
    *   **Type**: Integer
    *   **Constraints**: Foreign Key (links to User entity)
    *   **Description**: Identifier of the user who owns this task.
*   **`title`**:
    *   **Type**: String
    *   **Constraints**: Required, Cannot be empty
    *   **Description**: The name or brief description of the task.
*   **`description`**:
    *   **Type**: String
    *   **Constraints**: Optional
    *   **Description**: Additional details or notes for the task.
*   **`status`**:
    *   **Type**: Enum (String)
    *   **Constraints**: Values: "pending", "completed", "in progress", "archived", Default: "pending"
    *   **Description**: The current state of the task.
*   **`priority`**:
    *   **Type**: Enum (String)
    *   **Constraints**: Values: "low", "medium", "high"
    *   **Description**: The priority level of the task.
*   **`tags`**:
    *   **Type**: List of Strings
    *   **Constraints**: Optional
    *   **Description**: One or more labels (e.g., "work", "home", "urgent") associated with the task. Stored inline.
*   **`due_date`**:
    *   **Type**: Datetime
    *   **Constraints**: Optional, Must be a future date when provided
    *   **Description**: The deadline for the task.
*   **`recurrence`**:
    *   **Type**: String
    *   **Constraints**: Optional, Values: "daily", "weekly", "monthly"
    *   **Description**: Defines if and how often the task should recur.
*   **`created_at`**:
    *   **Type**: Datetime
    *   **Constraints**: Auto-timestamp (set on creation)
    *   **Description**: Timestamp indicating when the task was created.
*   **`updated_at`**:
    *   **Type**: Datetime
    *   **Constraints**: Auto-timestamp (updated on modification)
    *   **Description**: Timestamp indicating when the task was last updated.

### User

**Description**: Represents an authenticated individual who owns a collection of tasks.

**Attributes**:

*   **`id`**:
    *   **Type**: Integer
    *   **Constraints**: Primary Key, Unique
    *   **Description**: Unique identifier for the user. (Assumed to be managed by an external authentication system, referenced here as a Foreign Key).

## Relationships

*   **User to Task**: One-to-Many
    *   A User can have multiple Tasks.
    *   Each Task belongs to exactly one User (`user_id` is the foreign key).

## Validation Rules

*   `title` cannot be empty.
*   `status` must be one of: "pending", "completed", "in progress", "archived".
*   `priority` must be one of: "low", "medium", "high".
*   `recurrence` must be one of: "daily", "weekly", "monthly", or null.
*   `due_date` must be a future date when provided.
*   `user_id` must link to an existing User.
*   Data encryption at rest and in transit for all sensitive task-related data.
