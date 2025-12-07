# Tasks: Task Priority System

**Input**: Design documents from `/specs/001-task-priority/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*No specific setup tasks are needed as the `rich` library is already a dependency and the project structure is established.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 Define `Priority` Enum in `src/models.py` with values Low, Medium, High.
- [x] T002 Update `Task` model in `src/models.py` to include an optional `priority` attribute, defaulting to `None`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task with Priority (Priority: P1) 🎯 MVP

**Goal**: Allow users to assign a priority level to a task during creation, and store it in memory.

**Independent Test**: Create a task with and without priority, then verify the stored priority.

### Implementation for User Story 1

- [x] T003 [US1] Modify `add_task` function in `src/commands.py` to prompt for priority after title and description.
- [ ] T004 [US1] Implement logic in `src/commands.py` to parse user input for priority (Low, Medium, High, or empty).
- [x] T005 [US1] Pass the selected priority to the task creation logic in `src/storage.py`.
- [x] T006 [US1] Update `add_task` method in `src/storage.py` to accept and store the `priority` attribute for a task.
- [x] T007 [US1] Modify `list_tasks` function in `src/commands.py` to display the priority of each task.
- [x] T008 [US1] Integrate `rich` library in `src/commands.py` (or `src/app.py`/`src/main.py` if display logic is centralized) to display priorities with distinct colors (e.g., High=red, Medium=yellow, Low=green, None=grey).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T009 Add robust error handling for invalid priority input during task creation in `src/commands.py`.
- [x] T010 Ensure consistent display of priority (or lack thereof) across all task listing views.

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

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tasks T003, T004, T005, T006, T007, T008 within User Story 1 can be developed sequentially.

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Define Priority Enum in src/models.py"
Task: "Update Task model in src/models.py"
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
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
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
