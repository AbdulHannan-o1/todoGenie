# ADR-0003: Database Technology

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-10
- **Feature:** 001-phase2-web-app-init
- **Context:** The project requires a persistent and scalable relational database to store application data. Given the cloud-native focus and the need for a managed service, a serverless PostgreSQL solution is preferred.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   Database: Neon Serverless PostgreSQL

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   **Serverless:** Scales automatically with demand, reducing operational overhead and cost for fluctuating workloads.
-   **PostgreSQL Compatibility:** Leverages the robustness, flexibility, and rich feature set of PostgreSQL, a widely adopted and trusted relational database.
-   **Managed Service:** Neon handles database provisioning, maintenance, backups, and scaling, allowing developers to focus on application logic.
-   **Cost-Effective:** Pay-as-you-go model can be more economical for applications with variable usage patterns.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   **Vendor Lock-in:** Reliance on Neon as a specific cloud provider for the database service.
-   **Potential Latency:** Serverless nature might introduce slight cold-start latencies, though typically optimized for common use cases.
-   **Limited Control:** Less fine-grained control over database infrastructure compared to self-hosting.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **Alternative 1: Self-hosted PostgreSQL (e.g., on a VM or Docker):**
    -   Pros: Full control over the database environment, no vendor lock-in.
    -   Cons: Significant operational overhead for setup, maintenance, scaling, and backups; requires dedicated resources.
-   **Alternative 2: AWS RDS PostgreSQL / Google Cloud SQL PostgreSQL:**
    -   Pros: Managed service from major cloud providers, high availability, good integration with other cloud services.
    -   Cons: Not serverless (typically provisioned instances), potentially higher cost for low/variable usage, still some vendor lock-in.
-   **Alternative 3: MongoDB (NoSQL Database):**
    -   Pros: Flexible schema, good for rapidly evolving data models, scales horizontally well for certain workloads.
    -   Cons: Not relational, lacks ACID properties by default (can be configured), might be overkill for structured todo list data, requires different data modeling approach.

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
