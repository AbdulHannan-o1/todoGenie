# Implementation Plan: CLI Task Management

**Version**: 1.0
**Status**: In Progress
**Author**: Gemini
**Last Updated**: 2025-12-06

## 1. Technical Context

- **Technology Stack**: Python 3.10+ (Object-Oriented)
- **UI**: Full-fledged Terminal User Interface (TUI) using the `Textual` framework, built on `rich`, for interactive, in-place updates, arrow-key navigable menus, and rich styling.
- **Data Storage**: In-memory, as per the constitution.
- **Dependencies**: `rich`, `Textual`
- **Unknowns**:
  - Best practices for structuring an object-oriented Python TUI application with `Textual`.
  - Optimizing `Textual` applications for performance and responsiveness.

## 2. Constitution Check

- **I. Spec-First Design**: Compliant. The implementation will follow the provided spec.
- **II. CLI-First Interface**: Compliant. The application is a TUI.
- **III. In-Memory Storage**: Compliant. Data will be stored in-memory.
- **IV. CRUD and AI-Driven Enhancements**: Compliant. The plan covers the CRUD functionality.
- **V. Modular Architecture**: Compliant. The implementation will follow the specified modular architecture.
- **VI. Observability & User Feedback**: Compliant. The plan includes using `Textual` (which uses `rich`) for rich feedback.

## 3. Phase 0: Outline & Research

See `research.md` for details.

## 4. Phase 1: Design & Contracts

- **Data Model**: See `data-model.md`.
- **API Contracts**: Not applicable for this CLI application.
- **Quickstart**: See `quickstart.md`.

## 5. Phase 2: Implementation

This phase will be detailed in the `tasks.md` file.

## 9. TUI Framework Integration

This section outlines the architectural shift to a full-fledged Terminal User Interface (TUI) framework, `Textual`, to address the limitations of the previous interactive mode, particularly regarding UI updates and flickering.

### 9.1. Rationale for `Textual`

`Textual` is chosen for its robust capabilities in building modern TUIs, its foundation on the `rich` library (which we are already using), and its ability to provide:
-   **True in-place updates**: Only changed parts of the screen are redrawn, eliminating flickering.
-   **Widget-based UI**: Enables modular and reusable UI components for banners, task lists, and menus.
-   **Event-driven architecture**: Provides a structured way to handle user input (keyboard, mouse) and application logic.
-   **Scalability**: Offers a more maintainable and extensible framework for complex interactive terminal applications.

### 9.2. Architectural Changes

The `app.py` will be refactored to become a `Textual` application. This involves:
-   Defining a main `App` class inheriting from `textual.app.App`.
-   Implementing `Compose` methods to define the application's layout and widgets.
-   Handling user input and command execution through `Textual`'s message and action system.

### 9.3. UI Components within `Textual`

-   **Banner**: A dedicated `Textual` widget will display the "TODOGENIE" banner.
-   **Task List**: A `Textual` widget (e.g., `DataTable` or custom widget) will display tasks, updating in place as tasks are added, modified, or deleted. Conditional display (only if tasks exist) will be managed within this widget.
-   **Interactive Menu**: A `Textual` widget (e.g., `ListView` or custom widget) will provide arrow-key navigable menu options, with a clear visual indicator for the selected item and a default selection.
-   **Input Prompts**: `Textual`'s input widgets will be used for gathering user input (e.g., task descriptions, IDs).

### 9.4. Benefits

-   Elimination of UI flickering.
-   More responsive and intuitive user experience.
-   Improved code organization and maintainability for the UI layer.
-   Foundation for future advanced TUI features.
