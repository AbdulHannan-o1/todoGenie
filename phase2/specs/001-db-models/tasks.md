---

description: "Task list for Database & Models (SQLModel + Neon PostgreSQL) feature implementation"
---

# Tasks: Database & Models (SQLModel + Neon PostgreSQL)

**Input**: Design documents from `/specs/001-db-models/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure for backend/src/models, backend/src/db, backend/alembic, backend/tests/unit
- [X] T002 Configure Python environment and install primary dependencies (SQLModel, FastAPI, Alembic, Psycopg) in backend/requirements.txt
- [X] T003 Configure Alembic for database migrations in backend/alembic.ini and backend/alembic/env.py
- [X] T004 Create initial __init__.py files in backend/src and backend/src/db
- [X] T005 Create .env.example for DATABASE_URL in backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] Implement database engine creation and connection pooling in backend/src/db/engine.py
- [X] T007 [P] Implement dependency-based session injection in backend/src/db/session.py
- [X] T008 [P] Define base SQLModel for common attributes (created_at, updated_at) in backend/src/models/base.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Basic Todo Tasks (CRUD) (Priority: P1) 🎯 MVP

**Goal**: A user can create, view, update, and delete their todo tasks.

**Independent Test**: Can perform basic CRUD operations on tasks.

### Implementation for User Story 1

- [X] T009 [US1] Define Task SQLModel with id, user_id, title, description, status, priority, tags, due_date, recurrence, created_at, updated_at in backend/src/models/task.py
- [X] T010 [US1] Define TaskCreate, TaskUpdate, TaskRead Pydantic schemas in backend/src/models/task.py
- [X] T011 [US1] Implement database operations for creating a task in backend/src/services/task_service.py
- [X] T012 [US1] Implement database operations for reading a single task by ID in backend/src/services/task_service.py
- [X] T013 [US1] Implement database operations for updating a task by ID in backend/src/services/task_service.py
- [X] T014 [US1] Implement database operations for deleting a task by ID in backend/src/services/task_service.py
- [X] T015 [US1] Create API endpoint POST /tasks for creating tasks in backend/src/routes/tasks.py
- [X] T016 [US1] Create API endpoint GET /tasks/{task_id} for reading a single task in backend/src/routes/tasks.py
- [X] T017 [US1] Create API endpoint PUT /tasks/{task_id} for updating tasks in backend/src/routes/tasks.py
- [X] T018 [US1] Create API endpoint DELETE /tasks/{task_id} for deleting tasks in backend/src/routes/tasks.py
- [X] T019 [US1] Implement basic unit tests for Task model in backend/tests/unit/test_models.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Organize Tasks with Priority and Tags (Priority: P2)

**Goal**: Users can categorize and prioritize their tasks using priority levels and tags, and filter/sort by these attributes.

**Independent Test**: Can assign priority/tags, filter by priority/tag, sort by priority/due date.

### Implementation for User Story 2

- [X] T020 [US2] Update Task SQLModel to include status, priority, tags, due_date, recurrence fields in backend/src/models/task.py
- [X] T021 [US2] Update TaskCreate, TaskUpdate schemas to include status, priority, tags, due_date, recurrence in backend/src/models/task.py
- [X] T022 [US2] Implement database operations for listing tasks with filtering by status, priority, tags, due_date_before, due_date_after in backend/src/services/task_service.py
- [X] T023 [US2] Implement database operations for listing tasks with sorting by priority, due_date, title, created_at in backend/src/services/task_service.py
- [X] T024 [US2] Update API endpoint GET /tasks to include filtering and sorting parameters in backend/src/routes/tasks.py
- [X] T025 [US2] Implement unit tests for filtering and sorting logic in backend/tests/unit/test_task_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Schedule and Automate Recurring Tasks (Priority: P3)

**Goal**: Users can define tasks that automatically regenerate at specified intervals.

**Independent Test**: Can set recurrence, and new task instances are generated as expected.

### Implementation for User Story 3

- [X] T026 [US3] Implement logic for generating new task instances based on recurrence in backend/src/services/recurrence_service.py
- [X] T027 [US3] Integrate recurrence logic into task completion/due date checks in backend/src/services/task_service.py
- [X] T028 [US3] Implement unit tests for recurrence logic in backend/tests/unit/test_recurrence_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T029 Implement data encryption at rest and in transit (e.g., configure PostgreSQL for SSL, consider column-level encryption if needed) in backend/src/db/engine.py
- [X] T030 Implement error handling and logging for database operations in backend/src/db/session.py and backend/src/services/task_service.py
- [X] T031 Implement user deletion handling (reassign tasks to a "deleted user" data collection) in backend/src/services/user_service.py
- [X] T032 Review and optimize database queries for performance under expected load (2000 users, 100 tasks/user)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
# Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
# Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
# Task: "Create [Entity1] model in src/models/[entity1].py"
# Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
