# ADR-0005: Data Layer Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-11
- **Feature:** 001-db-models
- **Context:** The project requires a robust and scalable data layer for the TodoGenie application, aligning with the existing monorepo architecture and web-first API interface. The decision involves selecting core technologies for ORM, database, migrations, and language runtime to support task management features.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   ORM: SQLModel
-   Database: Neon Serverless PostgreSQL
-   Migrations: Alembic
-   Language: Python 3.12+
-   Validation: Pydantic (via SQLModel)
-   PostgreSQL Driver: Psycopg

## Consequences

### Positive

-   **SQLModel**: Provides a unified approach for data modeling and validation, reducing boilerplate and ensuring type safety. Leverages SQLAlchemy's power with Pydantic's schema capabilities.
-   **Neon Serverless PostgreSQL**: Offers a scalable, managed, and cost-effective database solution with good performance characteristics.
-   **Alembic**: Standardized and robust tool for managing database schema changes, ensuring smooth evolution of the data model.
-   **Python 3.12+**: Modern, performant, and widely supported language for backend development.
-   **Pydantic**: Ensures strong data validation and serialization, crucial for API integrity.
-   **Psycopg**: Reliable and performant PostgreSQL driver.
-   **Alignment with Constitution**: Directly fulfills the "Persistent Database Storage" principle.

### Negative

-   **Learning Curve**: Developers new to SQLModel or Alembic may require ramp-up time.
-   **Vendor Lock-in (Neon)**: While flexible, reliance on a specific serverless database provider introduces some level of vendor lock-in.
-   **Complexity**: Integrating multiple tools (SQLModel, Alembic, FastAPI) requires careful configuration and understanding.

## Alternatives Considered

-   **Alternative ORM**: SQLAlchemy Core (rejected for lack of Pydantic integration and higher boilerplate), Django ORM (rejected for being a full framework, not just an ORM), raw SQL (rejected for increased development time, error proneness, and lack of type safety).
-   **Alternative Database**: SQLite (rejected for lack of scalability and multi-user support), traditional PostgreSQL (rejected for higher operational overhead compared to serverless).
-   **Alternative Migrations**: Manual SQL scripts (rejected for being error-prone and difficult to manage in a team environment).

## References

- Feature Spec: `specs/001-db-models/spec.md`
- Implementation Plan: `specs/001-db-models/plan.md`
- Related ADRs: `0003-database-technology.md`
- Evaluator Evidence: