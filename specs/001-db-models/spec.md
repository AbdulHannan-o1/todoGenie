# Feature Specification: Database & Models (SQLModel + Neon PostgreSQL)

**Feature Branch**: `001-db-models`  
**Created**: 2025-12-11  
**Status**: Draft  
**Input**: User description: "SPEC 2 — Database & Models (SQLModel + Neon PostgreSQL) 1. Purpose Define the complete data layer for Phase 2 of the Todo App. This includes: Task model with all fields needed for core, intermediate, and advanced features. Optional Tag model. Database connection setup. Session handling. Migration strategy. This spec ensures that all features (CRUD, search, filters, sorting, recurring tasks, due dates, reminders) are supported structurally. 2. Task Model Specification Task Model Fields Field Type Description id int (PK) Unique identifier user_id int (FK) Links task to the authenticated user title str Task name; required description Optional[str] Additional details completed bool = False Completion state priority enum("low", "medium", "high") Task priority level tags List[str] One or more labels (work, home, urgent) due_date Optional[datetime] Deadline for the task recurrence Optional[str] Values: daily, weekly, monthly created_at datetime Auto timestamp updated_at datetime Auto timestamp Recurrence Field Behavior If set, the system should regenerate a new task instance once the current one is completed or past due_date. 3. Tag Model Specification (Optional) Tag Model (only if using a separate table): id: int name: str user_id: int (FK) Pivot Table (TaskTag): task_id tag_id If tags remain inline (List[str]), this section can be skipped. 4. SQLModel Implementation Requirements Use SQLModel for ORM + schema models. Create separate models for: Task (DB model) TaskCreate (input schema) TaskUpdate (partial update schema) TaskRead (response schema) Enable automatic timestamp update via event listeners or default factories. 5. Database Setup (Neon PostgreSQL) Requirements Use Neon Serverless PostgreSQL. Store connection URL in .env as: DATABASE_URL=postgresql+psycopg://<user>:<pass>@<host>/<db> Engine Configuration Create engine with connection pooling: engine = create_engine(DATABASE_URL, echo=True) Session Handling Use dependency-based session injection: with Session(engine) as session: yield session 6. Migration Strategy Requirements Use Alembic + SQLModel migration pattern. Setup auto-generation of migrations. Use alembic.ini + env.py configured for SQLModel. Migrations to include Create tasks table Add tags column or join table Add recurrence column Add user_id foreign key 7. Constraints & Validation Rules title cannot be empty. priority must be one of: low, medium, high. recurrence must be: daily, weekly, monthly, or null. due_date must be a future date when provided. user_id links tasks to owners. 8. How This Supports All Features Basic Level Add / Delete / Update / View / Complete → uses basic fields. Intermediate Level Priority → priority Tags → tags or Tag table Search → title, description Filter → completed, priority, tags, due_date Sort → priority, due_date, title, created_at Advanced Level Recurring Tasks → recurrence Due Dates → due_date Reminders → due_date, timestamps 9. Deliverables /backend/models/task.py /backend/db/session.py /backend/db/engine.py /backend/migrations/ All fields and decisions here must be implemented exactly before writing backend routes."

## User Scenarios & Testing

### User Story 1 - Manage Basic Todo Tasks (CRUD) (Priority: P1)

A user needs to be able to create, view, update, and delete their todo tasks. This forms the fundamental interaction with the application.

**Why this priority**: This is the core functionality of any todo application. Without basic task management, the application serves no purpose.

**Independent Test**: A user can fully test this by creating a new task, verifying its presence, modifying its details, marking it complete, and finally deleting it. This delivers the core value of task tracking.

**Acceptance Scenarios**:

1.  **Given** a user is logged in, **When** they create a new task with a title, **Then** the task is successfully saved and displayed in their task list.
2.  **Given** an existing task, **When** the user updates its title, description, or completion status, **Then** the changes are persisted and reflected in the task's details.
3.  **Given** an existing task, **When** the user deletes the task, **Then** the task is permanently removed from their task list.

### User Story 2 - Organize Tasks with Priority and Tags (Priority: P2)

Users need to categorize and prioritize their tasks to better manage their workload. This includes assigning priority levels and custom tags, and then being able to filter and sort tasks based on these attributes.

**Why this priority**: This enhances the usability and effectiveness of the todo application beyond simple listing, allowing for more sophisticated personal organization.

**Independent Test**: A user can test this by creating several tasks, assigning different priorities and tags to them, and then using filtering and sorting options to verify that tasks are displayed according to the selected criteria.

**Acceptance Scenarios**:

1.  **Given** a task, **When** the user assigns a priority level (low, medium, high) and/or one or more tags (e.g., "work", "home", "urgent"), **Then** these attributes are successfully associated with the task.
2.  **Given** multiple tasks with varying priorities and tags, **When** the user applies a filter based on a specific priority or tag, **Then** only tasks matching the filter criteria are displayed.
3.  **Given** multiple tasks, **When** the user sorts their task list by priority or due date, **Then** the tasks are ordered correctly according to the chosen sorting method.

### User Story 3 - Schedule and Automate Recurring Tasks (Priority: P3)

For routine activities, users need the ability to define tasks that automatically regenerate at specified intervals, ensuring continuity without manual re-creation.

**Why this priority**: This provides an advanced automation feature that significantly reduces manual effort for repetitive tasks, improving long-term task management efficiency.

**Independent Test**: A user can test this by creating a recurring task with a due date, marking the current instance as complete, and then observing the system automatically generate a new instance of that task for the next recurrence period.

**Acceptance Scenarios**:

1.  **Given** a task, **When** the user sets a recurrence pattern (daily, weekly, monthly) and a due date, **Then** the task is configured for automatic regeneration.
2.  **Given** a recurring task that has been marked as completed or whose `due_date` has passed, **When** the system processes recurrence logic, **Then** a new instance of that task is automatically created with an updated `due_date` based on the recurrence pattern.

### Edge Cases

-   **Empty Task Title**: What happens when a user attempts to create or update a task with an empty title? The system should prevent this.
-   **Invalid Priority/Recurrence**: How does the system handle attempts to set a task's priority or recurrence to a value not defined in the allowed enumerations? The system should reject invalid values.
-   **Past Due Date for New Task**: What occurs if a user tries to set a `due_date` in the past for a new task? The system should require `due_date` to be in the future.
-   **User Deletion with Associated Tasks**: If a user with existing tasks is deleted, their tasks will be reassigned to a designated "deleted user" data collection within the database. The original user's details relevant to the task (e.g., `user_id`) will be preserved within the task's data or in this dedicated collection for auditing/archival purposes.

## Requirements

### Functional Requirements

-   **FR-001**: The system MUST store tasks with the following attributes: `id` (unique identifier, primary key), `user_id` (foreign key linking to user), `title` (string, required), `description` (optional string), `status` (enum: "pending", "completed", "in progress", "archived", default "pending"), `priority` (enum: "low", "medium", "high"), `tags` (list of strings), `due_date` (optional datetime), `recurrence` (optional string: "daily", "weekly", "monthly"), `created_at` (datetime, auto-timestamp), and `updated_at` (datetime, auto-timestamp).
-   **FR-002**: The system MUST provide mechanisms for creating, reading, updating, and deleting tasks.
-   **FR-003**: The system MUST ensure that a task's `title` cannot be empty.
-   **FR-004**: The system MUST validate that a task's `priority` is one of "low", "medium", or "high".
-   **FR-005**: The system MUST validate that a task's `recurrence` is one of "daily", "weekly", "monthly", or null.
-   **FR-006**: The system MUST ensure that if a `due_date` is provided for a task, it must be a future date.
-   **FR-007**: The system MUST establish a foreign key relationship between tasks and users via `user_id`, ensuring tasks are linked to their respective owners.
-   **FR-008**: The system MUST utilize SQLModel for defining ORM models and Pydantic schemas for data validation and serialization (Task, TaskCreate, TaskUpdate, TaskRead).
-   **FR-009**: The system MUST automatically set `created_at` upon task creation and update `updated_at` on every task modification.
-   **FR-010**: The system MUST use Neon Serverless PostgreSQL as the primary database.
-   **FR-011**: The system MUST configure database connections with connection pooling for efficient resource management.
-   **FR-012**: The system MUST implement database schema migrations using Alembic, configured to work with SQLModel, to manage changes to the database structure.
-   **FR-013**: The system MUST automatically generate a new task instance for recurring tasks once the current instance is marked `completed` or its `due_date` has passed.
-   **FR-014**: The system MUST allow tasks to transition between the following states: "pending", "in progress", "completed", and "archived".
-   **FR-015**: The system MUST ensure data encryption at rest and in transit for all sensitive task-related data.

### Key Entities

-   **Task**: Represents a single unit of work or an item on a user's todo list. It encapsulates all the attributes defined in FR-001.
-   **Tag**: (Optional, if separate table) Represents a categorical label that can be applied to tasks for organization and filtering.
-   **User**: Represents an authenticated individual who owns a collection of tasks. Tasks are linked to users via the `user_id` foreign key.

## Out of Scope

The following features are not the responsibility of the data layer and are therefore out of scope:

-   Direct UI rendering or frontend logic
-   Authentication and authorization flows
-   Business logic such as recurring task generation
-   Notification scheduling and reminder triggers
-   External API integrations
-   Complex reporting, analytics, or dashboards
-   User management (beyond storing user_id reference)
-   Sorting & filtering logic (handled at service layer or query layer)
-   Validation beyond basic DB schema constraints

## Success Criteria

### Measurable Outcomes

-   **SC-001**: Users can successfully create, read, update, and delete tasks with all specified attributes.
-   **SC-002**: Users can effectively filter tasks by `completed` status, `priority`, `tags`, and `due_date`, and sort tasks by `priority`, `due_date`, `title`, and `created_at`.
-   **SC-003**: Recurring tasks are automatically regenerated within 1 hour of their current instance being completed or past due, for 100% of applicable tasks.
-   **SC-004**: The data layer correctly stores and retrieves all task-related information, maintaining data integrity and adhering to all defined constraints (e.g., non-empty title, valid priority, future due dates).
-   **SC-005**: Database migrations can be applied and rolled back successfully without data loss or corruption.
-   **SC-006**: All task CRUD operations (create, read, update, delete) complete with sub-second latency, and the system supports high throughput for these operations.
-   **SC-007**: The system efficiently handles a load of up to 2000 users, each with an average of 100 tasks, without significant performance degradation.

## Clarifications

### Session 2025-12-11

- Q: What are the target performance metrics for task operations (e.g., latency for CRUD, throughput)? → A: Sub-second latency, high throughput.
- Q: Are there other task states beyond 'completed' (e.g., 'pending', 'in progress', 'archived') that the system should support? → A: Yes, 'pending', 'completed', 'in progress', 'archived'.
- Q: Are there any explicit features or functionalities that are out of scope for this data layer? → A: Direct UI rendering, authentication/authorization, business logic (recurring task generation), notification scheduling, external API integrations, complex reporting, user management (beyond user_id reference), sorting/filtering logic, validation beyond basic DB schema constraints.
- Q: What is the expected number of tasks per user and total users? → A: 100 tasks/user, 2000 users.
- Q: Are there specific security requirements for data encryption (at rest/in transit) or access control beyond user ownership that the data layer needs to address? → A: Yes, data encryption at rest and in transit.