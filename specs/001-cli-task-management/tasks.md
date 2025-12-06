# Tasks: CLI Task Management

**Version**: 1.0
**Status**: In Progress
**Author**: Gemini
**Last Updated**: 2025-12-06

## Phase 1: Setup

- [X] T001 Create the project directory structure: `app.py`, `commands.py`, `storage.py`, `spec.py`, `utils.py`
- [X] T002 Initialize a virtual environment and install the `rich` library.

## Phase 2: Foundational

- [X] T003 [P] Implement the `Task` class in `spec.py` as per the data model.
- [X] T004 Implement the in-memory task storage in `storage.py`.

## Phase 3: User Story 1 - Create a new task

- [X] T005 [US1] Implement the `add` command in `commands.py`.
- [X] T006 [US1] Integrate the `add` command into `app.py`.

## Phase 4: User Story 2 - View all tasks

- [X] T007 [US2] Implement the `list` command in `commands.py`.
- [X] T008 [US2] Implement a function in `utils.py` to display tasks in a `rich` table.
- [X] T009 [US2] Integrate the `list` command into `app.py`.

## Phase 5: User Story 3 - Update an existing task

- [X] T010 [US3] Implement the `update` command in `commands.py`.
- [X] T011 [US3] Integrate the `update` command into `app.py`.

## Phase 6: User Story 4 - Mark a task as complete

- [X] T012 [US4] Implement the `complete` command in `commands.py`.
- [X] T013 [US4] Integrate the `complete` command into `app.py`.

## Phase 7: User Story 5 - Delete a task

- [X] T014 [US5] Implement the `delete` command in `commands.py`.
- [X] T015 [US5] Use `rich.prompt.Confirm` in `utils.py` for delete confirmation.
- [X] T016 [US5] Integrate the `delete` command into `app.py`.

## Phase 8: User Story 6 - Handle non-existent tasks

- [X] T017 [US6] Add error handling for non-existent tasks to the `update`, `complete`, and `delete` commands in `commands.py`.

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T018 Implement the `help` command in `app.py`.
- [X] T019 Add docstrings and type hints to all functions and classes.
- [X] T020 Create a `README.md` for the project.

## Dependencies

- User Stories 3, 4, 5, and 6 depend on User Story 2 (to view the tasks).
- User Story 1 is independent.

## Parallel Execution

- Tasks marked with `[P]` can be executed in parallel.
- Each user story phase can be worked on in parallel after the Foundational phase is complete, with the exception of the dependencies mentioned above.

## Implementation Strategy

The implementation will follow an MVP-first approach, starting with the core CRUD functionality (add, list) and then incrementally adding the other features.

## Phase 10: Interactive Mode

- [X] T021 [IM] Refactor `app.py` to support an interactive loop.
- [X] T022 [IM] Implement a main menu for interactive mode.
- [X] T023 [IM] Integrate `add` command into interactive mode.
- [X] T024 [IM] Integrate `list` command into interactive mode.
- [X] T025 [IM] Integrate `update` command into interactive mode.
- [X] T026 [IM] Integrate `complete` command into interactive mode.
- [X] T027 [IM] Integrate `delete` command into interactive mode.
- [X] T028 [IM] Implement an "exit" option for interactive mode.
- [X] T029 [IM] Display tasks automatically when entering interactive mode.

## Phase 11: Advanced Interactive UI

- [X] T030 [UI] Install `simple-term-menu` library.
- [X] T031 [UI] Refactor `app.py` to use `simple-term-menu` for interactive menu navigation.
- [X] T032 [UI] Configure `simple-term-menu` to display a green `>` indicator for the selected option.
- [X] T033 [UI] Ensure default selection is "add" in the interactive menu.

## Phase 12: UI Enhancements

- [X] T034 [UI] Implement "TODOGENIE" banner display on application start.
- [X] T035 [UI] Modify `interactive_mode` to conditionally display the task table only if tasks exist.
- [X] T036 [UI] Fix blinking issue for `help` and `list` commands in interactive mode.
- [X] T037 [UI] Add more `rich` styling and colors to output messages.

## Phase 13: UI Refresh

- [X] T038 [UI] Re-enable `clear_screen=True` in `TerminalMenu` and move task display logic.
- [X] T039 [UI] Add `console.clear()` at the beginning of each `while` loop iteration in `interactive_mode`.