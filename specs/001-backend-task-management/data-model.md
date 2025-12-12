# Data Model: Backend Task Management

## Entity: Task

Represents a single unit of work within the system.

### Attributes:

*   **`id`**:
    *   **Type**: Unique identifier (e.g., UUID or integer, auto-generated)
    *   **Constraints**: Primary Key, Not Null, Unique
*   **`title`**:
    *   **Type**: String
    *   **Constraints**: Not Null, Minimum length 1
    *   **Description**: A brief, descriptive name for the task.
*   **`description`**:
    *   **Type**: String
    *   **Constraints**: Nullable
    *   **Description**: Detailed explanation or additional notes for the task.
*   **`status`**:
    *   **Type**: String (Enum: 'pending', 'in progress', 'completed', 'archived', 'cancelled')
    *   **Constraints**: Not Null, Default: 'pending'
    *   **Description**: The current state of the task within its lifecycle.
*   **`priority`**:
    *   **Type**: String (Enum: 'low', 'medium', 'high')
    *   **Constraints**: Nullable, Default: 'medium'
    *   **Description**: The importance level of the task.
*   **`tags`**:
    *   **Type**: List of Strings (or JSONB array in PostgreSQL)
    *   **Constraints**: Nullable
    *   **Description**: Keywords for categorizing the task.
*   **`due_date`**:
    *   **Type**: Datetime (UTC)
    *   **Constraints**: Nullable
    *   **Description**: The date and time by which the task should be completed.
*   **`recurrence`**:
    *   **Type**: String (Enum: 'daily', 'weekly', 'monthly')
    *   **Constraints**: Nullable
    *   **Description**: Defines if and how often a task repeats.
*   **`user_id`**:
    *   **Type**: Unique identifier (e.g., UUID or integer)
    *   **Constraints**: Foreign Key referencing User entity, Not Null
    *   **Description**: The ID of the user who owns this task.

### Relationships:

*   **Task to User**: Many-to-One (Many Tasks belong to one User)

## Entity: User (Implicit from Authentication/Authorization)

Represents a user of the system.

### Attributes:

*   **`id`**:
    *   **Type**: Unique identifier (e.g., UUID or integer, auto-generated)
    *   **Constraints**: Primary Key, Not Null, Unique
*   **`username`**:
    *   **Type**: String
    *   **Constraints**: Not Null, Unique
*   **`email`**:
    *   **Type**: String
    *   **Constraints**: Not Null, Unique
*   **`password_hash`**:
    *   **Type**: String
    *   **Constraints**: Not Null
*   **`role`**:
    *   **Type**: String (Enum: 'Admin', 'Standard User')
    *   **Constraints**: Not Null, Default: 'Standard User'
    *   **Description**: The role of the user, determining their permissions.

### Relationships:

*   **User to Task**: One-to-Many (One User can have many Tasks)

## Task Lifecycle and State Transitions

The `status` attribute of a Task defines its current state. The following states and transitions are defined:

*   **States**:
    *   `Pending`: The task has been created but not yet started.
    *   `In Progress`: The task is currently being worked on.
    *   `Completed`: The task has been finished successfully.
    *   `Archived`: The task is no longer active but kept for historical purposes.
    *   `Cancelled`: The task was stopped before completion.

*   **Allowed Transitions**:
    *   `Pending` -> `In Progress`
    *   `Pending` -> `Cancelled`
    *   `In Progress` -> `Completed`
    *   `In Progress` -> `Cancelled`
    *   `Completed` -> `Archived`
    *   `Cancelled` -> `Archived`
    *   (Any state) -> `Archived` (for administrative archiving)
