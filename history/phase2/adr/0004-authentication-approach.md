# ADR-0004: Authentication Approach

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-10
- **Feature:** 001-phase2-web-app-init
- **Context:** The project requires a secure and scalable authentication mechanism for multi-user support. The frontend uses "Better Auth" (a JavaScript/TypeScript library), and the backend is FastAPI (Python). A method to bridge these two technologies for authentication is necessary.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   Approach: JWT (JSON Web Token) based authentication.
-   Frontend: Better Auth configured to issue JWT tokens.
-   Backend: FastAPI middleware to verify JWT tokens using a shared secret.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   **Stateless:** JWTs are self-contained, eliminating the need for the backend to store session information, which improves scalability.
-   **Decoupled:** Frontend and backend can independently verify authentication, reducing dependencies.
-   **Security:** Tokens can be short-lived and include expiration, reducing the risk of compromise.
-   **User Isolation:** Ensures each user only accesses their own data.
-   **Compatibility:** Bridges the gap between a JavaScript/TypeScript frontend authentication library and a Python backend.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   **Token Revocation:** Revoking individual JWTs before their natural expiration can be complex (requires blacklisting mechanisms).
-   **Token Size:** Large JWTs can increase request overhead.
-   **Secret Management:** Secure management of the shared secret key is critical; compromise of the secret compromises all tokens.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **Alternative 1: Session-based Authentication:**
    -   Pros: Simpler to implement token revocation, widely understood.
    -   Cons: Requires backend to maintain session state (less scalable), more complex cross-origin setup, not ideal for mobile or multi-service architectures.
-   **Alternative 2: OAuth 2.0 (e.g., using a dedicated identity provider like Auth0 or Keycloak):**
    -   Pros: Robust, industry-standard for delegated authorization, handles complex scenarios like social logins and multi-factor authentication.
    -   Cons: Overkill for initial project phase, significantly more complex to set up and manage, introduces external dependencies.
-   **Alternative 3: API Key Authentication:**
    -   Pros: Simple to implement for machine-to-machine communication.
    -   Cons: Not suitable for user authentication, less secure than JWTs for user sessions, no built-in expiration.

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
