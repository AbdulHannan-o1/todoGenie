# ADR-0002: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-10
- **Feature:** 001-phase2-web-app-init
- **Context:** The project requires a robust and scalable backend to serve the frontend application, manage data persistence, and handle business logic. A performant and developer-friendly framework is essential.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   Framework: FastAPI
-   ORM: SQLModel

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   FastAPI offers high performance (comparable to Node.js and Go) due to Starlette and Pydantic, making it suitable for high-throughput APIs.
-   Excellent developer experience with automatic interactive API documentation (Swagger UI/ReDoc) and strong type hints.
-   SQLModel provides a convenient way to define both Pydantic models and SQLAlchemy models in a single class, simplifying data validation and database interactions.
-   Python ecosystem provides a rich set of libraries for various backend needs.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   FastAPI and SQLModel are relatively newer compared to Django or Flask with SQLAlchemy, which might mean a smaller community or fewer readily available resources for very specific edge cases.
-   Python's Global Interpreter Lock (GIL) can limit true parallelism for CPU-bound tasks, though FastAPI's async nature mitigates this for I/O-bound operations.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **Alternative 1: Django + Django ORM:**
    -   Pros: Mature, batteries-included framework with a large community, extensive documentation, and built-in admin panel.
    -   Cons: Can be opinionated and heavier for simple APIs, potentially slower performance compared to FastAPI for certain workloads.
-   **Alternative 2: Flask + SQLAlchemy:**
    -   Pros: Lightweight and flexible microframework, allowing developers to choose components.
    -   Cons: Requires more manual setup and integration of various libraries compared to FastAPI's integrated approach, less opinionated which can lead to inconsistencies.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: `specs/001-phase2-web-app-init/spec.md`
- Implementation Plan: `specs/001-phase2-web-app-init/plan.md`
- Related ADRs: null
- Evaluator Evidence: null <!-- link to eval notes/PHR showing graders and outcomes -->
