# Data Model: Phase 2 Web Application Initialization

This document defines the initial data models for the Todo Genie application, focusing on the `User` and `Task` entities required for Phase 2.

## Entities

### User

Represents an application user. This model is fundamental for authentication and associating tasks with specific users.

-   **`id`**:
    *   **Type**: String (UUID)
    *   **Constraints**: Primary Key, Unique, Not Null
    *   **Description**: Unique identifier for the user.
-   **`email`**:
    *   **Type**: String
    *   **Constraints**: Unique, Not Null
    *   **Description**: User's email address, used for login.
-   **`hashed_password`**:
    *   **Type**: String
    *   **Constraints**: Not Null
    *   **Description**: Hashed password for security.
-   **`is_active`**:
    *   **Type**: Boolean
    *   **Constraints**: Default `True`, Not Null
    *   **Description**: Indicates if the user account is active.

### Task

Represents a single todo item, now associated with a specific user.

-   **`id`**:
    *   **Type**: Integer
    *   **Constraints**: Primary Key, Auto-increment
    *   **Description**: Unique identifier for the task.
-   **`user_id`**:
    *   **Type**: String (UUID)
    *   **Constraints**: Foreign Key referencing `User.id`, Not Null
    *   **Description**: Identifier of the user who owns this task.
-   **`title`**:
    *   **Type**: String
    *   **Constraints**: Not Null, Max Length 200
    *   **Description**: Brief title of the task.
-   **`description`**:
    *   **Type**: Text
    *   **Constraints**: Nullable, Max Length 1000
    *   **Description**: Detailed description of the task.
-   **`completed`**:
    *   **Type**: Boolean
    *   **Constraints**: Default `False`, Not Null
    *   **Description**: Status indicating if the task is completed.
-   **`created_at`**:
    *   **Type**: Timestamp
    *   **Constraints**: Default Current Timestamp, Not Null
    *   **Description**: Timestamp when the task was created.
-   **`updated_at`**:
    *   **Type**: Timestamp
    *   **Constraints**: Default Current Timestamp (on update), Not Null
    *   **Description**: Timestamp when the task was last updated.

## Relationships

-   **User to Task**: One-to-Many. A `User` can have multiple `Task`s, but each `Task` belongs to only one `User`. This relationship is enforced by the `user_id` foreign key in the `Task` model.
