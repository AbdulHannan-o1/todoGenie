# ADR-0011: Task Lifecycle Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-12
- **Feature:** 001-backend-task-management
- **Context:** The task management system requires a clear definition of task states and transitions to ensure predictable workflows and support future feature development.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Define a comprehensive task lifecycle with states: "Pending", "In Progress", "Completed", "Archived", and "Cancelled". Specify allowed transitions between these states.
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

## Consequences

### Positive

-   Clear and predictable task workflows.
-   Facilitates development of features dependent on task state.
-   Improved data consistency and integrity.

### Negative

-   Increased complexity in task state management logic.
-   Requires careful implementation of state transition rules.

## Alternatives Considered

-   **Simpler Task States (e.g., "Pending", "Completed")**: Rejected for limited expressiveness and inability to represent intermediate or administrative states.
-   **No Explicit Lifecycle**: Rejected for potential workflow inconsistencies and difficulty in managing task progression.

## References

- Feature Spec: /home/abdulhannan/data/development/openAi/todogenie/specs/001-backend-task-management/spec.md
- Implementation Plan: /home/abdulhannan/data/development/openAi/todogenie/specs/001-backend-task-management/plan.md
- Related ADRs: 0006-task-data-model-design.md (expands on task status)
- Evaluator Evidence: null