# ADR-0007: API Design for Task Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-11
- **Feature:** 001-db-models
- **Context:** The TodoGenie application requires a clear and consistent interface for interacting with task data. The API design needs to support CRUD operations, filtering, sorting, and pagination while adhering to established architectural principles.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **API Style**: RESTful API.
-   **Endpoints**:
    *   `POST /tasks`: Create a new task.
    *   `GET /tasks`: Retrieve a list of tasks (supports filtering by `status`, `priority`, `tags`, `due_date_before`, `due_date_after`; supports sorting by `priority`, `due_date`, `title`, `created_at`).
    *   `GET /tasks/{task_id}`: Retrieve a single task by its ID.
    *   `PUT /tasks/{task_id}`: Update an existing task by its ID.
    *   `DELETE /tasks/{task_id}`: Delete a task by its ID.
-   **Schemas**: `TaskCreate`, `TaskUpdate`, `TaskRead` (defined using SQLModel/Pydantic).
-   **Authentication**: All endpoints require authentication (implied by `user_id` in Task model and `constitution.md`).

## Consequences

### Positive

-   **Standardized**: Adheres to REST principles, making the API intuitive and easy to consume for frontend and other services.
-   **Comprehensive**: Covers all necessary CRUD operations and supports advanced querying (filtering, sorting).
-   **Type-Safe**: Leveraging Pydantic schemas ensures data consistency and reduces errors.
-   **Scalable**: Designed to handle a growing number of tasks and users with efficient querying.
-   **Aligned with Constitution**: Directly supports the "Web-First API Interface" and "RESTful CRUD" principles.

### Negative

-   **Over-fetching/Under-fetching**: For complex UI needs, REST can sometimes lead to over-fetching or under-fetching data, potentially requiring multiple requests.
-   **Versioning**: Requires careful versioning strategy for future API changes.

## Alternatives Considered

-   **GraphQL**: (Rejected for initial complexity) Offers more flexibility for clients to request specific data, but introduces a new query language and ecosystem, increasing initial development overhead.
-   **RPC (Remote Procedure Call)**: (Rejected for lack of standardization) Less standardized than REST, potentially leading to less discoverable and harder-to-integrate APIs.

## References

- Feature Spec: `specs/001-db-models/spec.md`
- Implementation Plan: `specs/001-db-models/plan.md`
- API Contracts: `specs/001-db-models/contracts/openapi.yaml`
- Related ADRs: `0005-data-layer-technology-stack.md`, `0006-task-data-model-design.md`
- Evaluator Evidence: