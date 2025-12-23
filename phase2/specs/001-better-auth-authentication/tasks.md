# Tasks: Better Auth Authentication

**Input**: Design documents from `/specs/001-better-auth-authentication/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `phase2/backend/src/`, `phase2/frontend/src/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install Python dependencies (FastAPI, SQLModel, Better Auth, psycopg, alembic, pytest) in `phase2/backend/requirements.txt`
- [X] T004 Create frontend project structure in `phase2/frontend/`
- [X] T005 Initialize Next.js project with TypeScript in `phase2/frontend/`
- [X] T006 Install Node.js dependencies (React, Next.js, Jest, React Testing Library, Cypress) in `phase2/frontend/package.json`
- [X] T007 Configure backend linting and formatting (e.g., Black, Flake8) in `backend/pyproject.toml`
- [X] T008 Configure frontend linting and formatting (e.g., ESLint, Prettier) in `phase2/frontend/.eslintrc.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Setup database connection and configuration in `phase2/backend/src/db.py`
- [X] T008 Define base SQLModel for User and Task entities in `phase2/backend/src/models.py`
- [X] T009 Setup Alembic for database migrations in `phase2/backend/alembic.ini`
- [X] T010 Create initial database migration for User and Task models in `phase2/backend/alembic/versions/`
- [X] T011 Implement basic authentication middleware for JWT token validation in `phase2/backend/src/auth.py`
- [X] T012 Configure global error handling and logging infrastructure in `phase2/backend/src/main.py`
- [X] T013 Setup base API routing for `/users` and `/tasks` in `phase2/backend/src/main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Signup (Priority: P1) 🎯 MVP

**Goal**: New user can successfully create an account.

**Independent Test**: A new user can navigate to the signup page, fill in their details, and successfully create an account. They should then be able to proceed to the login page.

- [X] T015 [P] [US1] Write frontend unit tests for signup form component in `phase2/frontend/tests/components/signup_form.test.tsx`
- [X] T016 [P] [US1] Write E2E test for successful user signup flow in `phase2/frontend/cypress/e2e/signup.cy.ts`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement password hashing utility in `phase2/backend/src/utils.py`
- [X] T018 [P] [US1] Implement user creation logic in `phase2/backend/src/services/user_service.py`
- [X] T019 [US1] Create `POST /users/register` endpoint in `phase2/backend/src/routes/users.py`
- [X] T020 [P] [US1] Design and implement signup page UI in `phase2/frontend/src/pages/signup.tsx`
- [X] T021 [US1] Implement signup form handling and API integration in `phase2/frontend/src/pages/signup.tsx`
- [X] T022 [US1] Add validation and error handling for signup form (FR-009) in `phase2/frontend/src/pages/signup.tsx`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: Registered user can successfully log in and obtain an access token.

**Independent Test**: A registered user can enter their credentials on the login page and gain access to their dashboard or task list.

### Tests for User Story 2

- [X] T023 [P] [US2] Write backend unit tests for user authentication logic in `phase2/backend/tests/test_auth.py`
- [X] T024 [P] [US2] Write frontend unit tests for login form component in `phase2/frontend/tests/components/login_form.test.tsx`
- [X] T025 [P] [US2] Write E2E test for successful user login flow in `phase2/frontend/cypress/e2e/login.cy.ts`

### Implementation for User Story 2

- [X] T026 [P] [US2] Implement JWT token generation and validation utilities in `phase2/backend/src/auth.py`
- [X] T027 [P] [US2] Implement user login logic in `phase2/backend/src/services/auth_service.py`
- [X] T028 [US2] Create `POST /users/login` endpoint in `phase2/backend/src/routes/auth.py`
- [X] T029 [P] [US2] Design and implement login page UI in `phase2/frontend/src/pages/login.tsx`
- [X] T030 [US2] Implement login form handling and API integration in `phase2/frontend/src/pages/login.tsx`
- [X] T031 [US2] Implement client-side token storage and retrieval in `phase2/frontend/src/utils/auth.ts`
- [X] T032 [US2] Add validation and error handling for login form (FR-009) in `phase2/frontend/src/pages/login.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Secure Task Access (Priority: P2)

**Goal**: Logged-in user can only access their own tasks.

**Independent Test**: A logged-in user attempts to access tasks belonging to another user and is denied access.

### Tests for User Story 3

- [X] T033 [P] [US3] Write backend unit tests for task authorization logic in `phase2/backend/tests/test_tasks.py`
- [X] T034 [P] [US3] Write E2E test for secure task access (e.g., attempting to view another user's task) in `phase2/frontend/cypress/e2e/secure_tasks.cy.ts`

### Implementation for User Story 3

- [X] T035 [P] [US3] Implement task CRUD operations in `phase2/backend/src/services/task_service.py`
- [X] T036 [US3] Create `GET /tasks`, `POST /tasks`, `GET /tasks/{task_id}`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}` endpoints in `phase2/backend/src/routes/tasks.py`
- [X] T037 [US3] Implement task ownership verification in `phase2/backend/src/services/task_service.py`
- [X] T038 [P] [US3] Design and implement task listing page UI in `phase2/frontend/src/pages/tasks.tsx`
- [X] T039 [P] [US3] Design and implement task detail/edit page UI in `phase2/frontend/src/pages/tasks/[id].tsx`
- [X] T040 [US3] Implement authenticated API calls for task management in `phase2/frontend/src/services/task_api.ts`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T041 [P] Implement user account state transitions (Active, Suspended, Deleted) (FR-007) in `phase2/backend/src/services/user_service.py`
- [X] T042 [P] Implement encryption of sensitive user data at rest (FR-008) in `phase2/backend/src/utils.py`
- [X] T043 [P] Implement `POST /users/logout` endpoint in `phase2/backend/src/routes/auth.py`
- [X] T044 [P] [US3] Implement client-side logout functionality in `phase2/frontend/src/utils/auth.ts`
- [X] T045 Review and refine error messages across backend and frontend (FR-009)
- [X] T046 Code cleanup and refactoring across the feature
- [X] T047 Update `quickstart.md` with any final setup or usage instructions
- [X] T048 Run all tests (unit, integration, E2E) to ensure full coverage and functionality

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
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
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
# Launch all tests for User Story 1 together:
- [X] T014 [P] [US1] Write backend unit tests for user registration logic in `phase2/backend/tests/test_users.py`
- [ ] T015 [P] [US1] Write frontend unit tests for signup form component in `phase2/frontend/tests/components/signup_form.test.tsx`
- [ ] T016 [P] [US1] Write E2E test for successful user signup flow in `phase2/frontend/cypress/e2e/signup.cy.ts`

# Launch parallel implementation tasks for User Story 1:
- [X] T017 [P] [US1] Implement password hashing utility in `phase2/backend/src/utils.py`
- [X] T018 [P] [US1] Implement user creation logic in `phase2/backend/src/services/user_service.py`
- [ ] T020 [P] [US1] Design and implement signup page UI in `phase2/frontend/src/pages/signup.tsx`
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
