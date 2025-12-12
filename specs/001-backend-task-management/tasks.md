# Tasks for Backend Task Management

**Feature Branch**: `001-backend-task-management` | **Date**: 2025-12-12
**Input**: Feature specification from `/specs/001-backend-task-management/spec.md`
**Plan**: `/specs/001-backend-task-management/plan.md`

## Summary

This document outlines the detailed implementation tasks for the Backend Task Management feature, organized into phases based on user story priorities and cross-cutting concerns. Each task is designed to be actionable and independently testable where possible.

## Implementation Strategy

The project will follow an MVP-first approach, delivering User Story 1 (Manage Basic Tasks) as the initial functional increment. Subsequent user stories will be delivered incrementally, building upon the foundational features. Parallelization opportunities are identified to optimize development.

## Dependency Graph (User Story Completion Order)

*   Phase 1 (Setup) -> Phase 2 (Foundational)
*   Phase 2 (Foundational) -> Phase 3 (US1)
*   Phase 3 (US1) -> Phase 4 (US2)
*   Phase 3 (US1) -> Phase 5 (US3)
*   Phase 4 (US2) -> Phase 6 (Polish)
*   Phase 5 (US3) -> Phase 6 (Polish)

## Parallel Execution Examples per User Story

*   **User Story 1 - Manage Basic Tasks**:
    *   T014, T015, T016, T017, T018, T019, T020, T021, T022 can be implemented in parallel once foundational tasks are complete.
*   **User Story 2 - Search, Filter, and Sort Tasks**:
    *   T023, T024, T025, T026, T027, T028 can be implemented in parallel once US1 is complete.
*   **User Story 3 - Manage Recurring Tasks and Reminders**:
    *   T029, T030, T031, T032, T033, T034, T035 can be implemented in parallel once US1 is complete.

---

## Phase 1: Setup Tasks (Project Initialization)

**Goal**: Establish the basic project structure, database connection, authentication framework, and core models.

- [X] T001 Initialize FastAPI project structure in `backend/src/api/`
- [X] T002 Configure database connection with SQLModel and Neon Serverless PostgreSQL in `backend/src/db.py`
- [X] T003 Set up Alembic for database migrations in `backend/`
- [X] T004 Configure basic logging and error handling in `backend/src/utils/`
- [X] T005 Implement base User model with authentication fields in `backend/src/models/user.py`
- [X] T006 Implement base Task model with core attributes and relationships in `backend/src/models/task.py`
- [X] T007 Set up pytest for backend testing in `backend/tests/`

---

## Phase 2: Foundational Tasks (Blocking Prerequisites for all User Stories)

**Goal**: Implement core authentication, authorization, and a generic task CRUD service that all user stories will depend on.

- [X] T008 Implement basic authentication endpoints (`/auth/register`, `/auth/token`) in `backend/src/api/auth.py`
- [X] T009 Implement JWT token generation and validation in `backend/src/auth/jwt.py` (Integrated into T008)
- [X] T010 Implement role-based access control (RBAC) middleware in `backend/src/middleware/rbac.py`
- [X] T011 Implement user authentication and authorization logic in `backend/src/services/user_service.py`
- [X] T012 Integrate authentication middleware into FastAPI application in `backend/src/main.py`
- [X] T013 Implement a generic CRUD service for tasks in `backend/src/services/task_crud_service.py`

---

## Phase 3: User Story 1 - Manage Basic Tasks (Priority: P1)

**Goal**: Enable users to perform fundamental CRUD operations on tasks, including marking them as complete, with proper validation and error handling.

**Independent Test Criteria**: A user can successfully create, view, update, delete, and mark a task as complete via the API, and all operations return expected results or errors.

- [X] T014 [P] [US1] Implement `TaskCreate` and `TaskUpdate` schemas in `backend/src/schemas/task.py`
- [X] T015 [P] [US1] Implement `POST /tasks` endpoint for creating tasks in `backend/src/api/tasks.py`
- [X] T016 [P] [US1] Implement `GET /tasks/{id}` endpoint for retrieving a single task in `backend/src/api/tasks.py`
- [X] T017 [P] [US1] Implement `PUT /tasks/{id}` endpoint for updating tasks in `backend/src/api/tasks.py`
- [X] T018 [P] [US1] Implement `DELETE /tasks/{id}` endpoint for deleting tasks in `backend/src/api/tasks.py`
- [X] T019 [P] [US1] Implement `PATCH /tasks/{id}/complete` endpoint for marking tasks as complete in `backend/src/api/tasks.py`
- [X] T020 [US1] Implement title validation (not empty) for task creation/update in `backend/src/schemas/task.py`
- [X] T021 [US1] Implement 404 error handling for non-existent tasks in `backend/src/api/tasks.py`
- [X] T022 [US1] Implement consistent JSON error responses in `backend/src/main.py` or `backend/src/utils/error_handlers.py`

---

## Phase 4: User Story 2 - Search, Filter, and Sort Tasks (Priority: P2)

**Goal**: Provide users with advanced capabilities to search, filter, and sort their tasks based on various criteria.

**Independent Test Criteria**: A user can successfully query tasks using search keywords, filter by priority, tag, or status, and sort the results by specified criteria, receiving accurate and relevant task lists.

- [X] T023 [P] [US2] Implement `GET /tasks` endpoint for listing all tasks with query parameters in `backend/src/api/tasks.py`
- [X] T024 [US2] Implement query parameter parsing for search, filter, and sort in `backend/src/api/tasks.py`
- [X] T025 [US2] Implement search logic (keyword in title/description) in `backend/src/services/task_query_service.py`
- [X] T026 [US2] Implement filter logic (priority, tag, status) in `backend/src/services/task_query_service.py`
- [X] T027 [US2] Implement sort logic (priority, due\_date, alpha) in `backend/src/services/task_query_service.py`
- [X] T028 [US2] Integrate query filtering into `GET /tasks` endpoint in `backend/src/api/tasks.py`

---

## Phase 5: User Story 3 - Manage Recurring Tasks and Reminders (Priority: P3)

**Goal**: Enable users to define recurring tasks and receive timely reminders via browser notifications and WhatsApp messages.

**Independent Test Criteria**: A user can create a recurring task, observe its auto-generation, and receive browser and WhatsApp reminders as scheduled.

-   [X] T029 [US3] Update Task model to include `recurrence` field in `backend/src/models/task.py`
-   [X] T030 [US3] Implement logic for auto-generating next occurrence of recurring tasks in `backend/src/services/recurring_task_service.py`
- [X] T031 [US3] Implement logic for creating recurring tasks in `backend/src/services/task_scheduling_service.py`
- [X] T032 [US3] Implement a background job for sending task reminders in `backend/src/jobs/reminder_job.py`
- [X] T033 [US3] Integrate background job scheduler (e.g., `apscheduler`) into FastAPI application in `backend/src/main.py`
- [X] T034 [US3] Implement `POST /tasks/{id}/reminders` endpoint for creating custom reminders in `backend/src/api/tasks.py`
- [X] T035 [US3] Implement logic for triggering reminder notifications for tasks with due dates in `backend/src/services/notification_service.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Ensure the overall quality, testability, and maintainability of the backend system.

-   [X] T036 Implement comprehensive unit tests for all services and API endpoints in `backend/tests/`
-   [X] T037 Implement integration tests for API endpoints in `backend/tests/`
-   [X] T038 Document API with updated OpenAPI specification in `contracts/openapi.yaml`
-   [X] T039 Update `quickstart.md` with complete API interaction examples and setup instructions
-   [X] T040 Review and refine error messages and logging across the backend
-   [X] T041 Implement user role management endpoints (e.g., `POST /users/{id}/role`) in `backend/src/api/users.py`
-   [X] T042 Implement data encryption at rest and in transit (if not handled by PostgreSQL/infrastructure) in `backend/src/utils/security.py`
