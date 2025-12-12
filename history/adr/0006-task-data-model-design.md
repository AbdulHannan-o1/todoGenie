# ADR-0006: Task Data Model Design

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-11
- **Feature:** 001-db-models
- **Context:** The core of the TodoGenie application revolves around managing user tasks. A well-defined and flexible data model is crucial to support current functional requirements (CRUD, priority, tags, recurrence, due dates, task states) and allow for future extensions.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **Task Entity**:
    *   Attributes: `id` (PK), `user_id` (FK), `title`, `description`, `status` (enum: "pending", "completed", "in progress", "archived"), `priority` (enum: "low", "medium", "high"), `tags` (List[str] - inline), `due_date`, `recurrence`, `created_at`, `updated_at`.
    *   Validation: `title` not empty, `status` enum, `priority` enum, `recurrence` enum/null, `due_date` future (if provided).
-   **User Entity**: `id` (PK) - referenced as FK in Task.
-   **Relationship**: One-to-many (User to Task).
-   **User Deletion Handling**: Tasks of a deleted user are reassigned to a designated "deleted user" data collection, preserving original user details for auditing/archival.

## Consequences

### Positive

-   **Comprehensive**: Supports all defined functional requirements for task management.
-   **Flexible**: Inline tags simplify initial implementation while allowing for future migration to a separate Tag entity if needed.
-   **Clear State Management**: Explicit `status` enum provides clear task lifecycle.
-   **Data Integrity**: Built-in validation rules and foreign key constraints ensure data quality.
-   **Scalability**: Designed to handle expected data volumes (100 tasks/user, 2000 users).

### Negative

-   **Inline Tags**: May become less efficient for complex tag management (e.g., global tag lists, tag metadata) in the future.
-   **User Deletion**: Reassigning tasks requires a dedicated mechanism for the "deleted user" data collection and potential adjustments to queries.

## Alternatives Considered

-   **Separate Tag Entity with Pivot Table**: (Rejected for initial complexity) Would provide more robust tag management (e.g., unique global tags, tag descriptions) but adds an extra table and join complexity for basic tagging.
-   **Boolean `completed` field**: (Rejected for limited expressiveness) Would only indicate completion, not other states like "pending" or "in progress", limiting task workflow visibility.
-   **Hard Delete User Tasks**: (Rejected for data loss) Would simplify deletion but lose historical task data, which might be valuable for auditing or analytics.

## References

- Feature Spec: `specs/001-db-models/spec.md`
- Implementation Plan: `specs/001-db-models/plan.md`
- Data Model: `specs/001-db-models/data-model.md`
- Related ADRs: `0005-data-layer-technology-stack.md`
- Evaluator Evidence: