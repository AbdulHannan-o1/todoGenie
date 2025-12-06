# Implementation Plan: CLI Task Management

**Version**: 1.0
**Status**: In Progress
**Author**: Gemini
**Last Updated**: 2025-12-06

## 1. Technical Context

- **Technology Stack**: Python 3.10+ (Object-Oriented)
- **UI**: Interactive, rich, colored command-line interface using the `rich` library for output and `simple-term-menu` for arrow-key navigable menu selection.
- **Data Storage**: In-memory, as per the constitution.
- **Dependencies**: `rich`, `simple-term-menu`
- **Unknowns**:
  - Best practices for structuring an object-oriented Python CLI application.
  - Best practices for using the `rich` library for CLI UI design.
  - Best practices for creating an interactive CLI with `rich` and `simple-term-menu`.

## 2. Constitution Check

- **I. Spec-First Design**: Compliant. The implementation will follow the provided spec.
- **II. CLI-First Interface**: Compliant. The application is a CLI.
- **III. In-Memory Storage**: Compliant. Data will be stored in-memory.
- **IV. CRUD and AI-Driven Enhancements**: Compliant. The plan covers the CRUD functionality.
- **V. Modular Architecture**: Compliant. The implementation will follow the specified modular architecture.
- **VI. Observability & User Feedback**: Compliant. The plan includes using the `rich` library for colored feedback.

## 3. Phase 0: Outline & Research

See `research.md` for details.

## 4. Phase 1: Design & Contracts

- **Data Model**: See `data-model.md`.
- **API Contracts**: Not applicable for this CLI application.
- **Quickstart**: See `quickstart.md`.

## 5. Phase 2: Implementation

This phase will be detailed in the `tasks.md` file.

## 6. Interactive Mode

The application will operate in an interactive loop, presenting a menu of options to the user that can be navigated using arrow keys. After each command execution, the menu will reappear, and the current list of tasks will be displayed.

### Interaction Flow:

1.  Application starts.
2.  If tasks exist, they are displayed in a `rich` table.
3.  A menu of available commands (add, list, update, complete, delete, help, exit) is presented, with an arrow (`>`) indicating the currently selected option.
4.  User navigates the menu using arrow keys (up/down) and selects a command by hitting Enter.
5.  Application prompts for necessary arguments (e.g., description for 'add', ID for 'delete').
6.  Command is executed.
7.  Tasks are displayed again (if applicable).
8.  Menu reappears.
9.  Loop continues until 'exit' command is chosen.

## 7. UI Enhancements

This section outlines further enhancements to the user interface to improve clarity and user experience.

### 7.1. "TODOGENIE" Banner

A prominent "TODOGENIE" banner will be displayed upon application startup to provide a clear branding and welcome message.

### 7.2. Conditional Task Display

The task table will only be displayed if there are active tasks. If the task list is empty, the table will be omitted to reduce clutter.

### 7.3. Blinking Fix for `help` and `list`

The issue where the screen "blinks" or redraws rapidly when `help` or `list` commands are executed will be addressed. This likely involves adjusting screen clearing behavior or ensuring output persistence.

### 7.4. Enhanced Color Usage

The application's output will be enhanced with additional `rich` styling and colors to improve readability and visual appeal. This includes:
-   Coloring messages (e.g., success, error, informational).
-   Potentially adding more color to the task table or menu.

## 8. UI Refresh

This section addresses the user's feedback regarding the cluttered output and aims to provide a cleaner, more "in-place" update experience.

### 8.1. Screen Clearing

To prevent the entire UI from being re-printed and pushed up the terminal, the screen will be cleared at the beginning of each interactive loop iteration. This ensures that the new display of tasks and the menu always starts from a clean slate.

### 8.2. `TerminalMenu` `clear_screen` Re-enablement

The `clear_screen=True` option in `simple-term-menu`'s `TerminalMenu` will be re-enabled. This, in conjunction with the explicit screen clearing, will ensure a consistent and clean redraw of the menu and tasks. The task display logic will be carefully placed to ensure it appears after the screen clear but before the menu is presented.