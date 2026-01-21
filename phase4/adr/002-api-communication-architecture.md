# ADR 002: API Communication Architecture Between Frontend and Backend Services

## Status
Accepted

## Date
2026-01-21

## Context
The frontend Next.js application needs to communicate with the backend FastAPI service in a Kubernetes environment. Initially, there were issues with the API communication due to double prefixing in routes and incorrect service routing. The architecture needs to handle both server-side and client-side API calls properly in a containerized environment.

## Decision
We decided to implement the following API communication architecture:

**Server-Side API Calls:**
- Next.js rewrites configured in `next.config.ts` to proxy API requests to backend service
- Rewrite rules map frontend API calls to backend service using Kubernetes DNS names
- Proper handling of authentication headers and cookies in proxy requests

**Client-Side API Calls:**
- Use relative paths for browser requests to trigger Next.js rewrites
- Axios client configured to use relative paths on the client-side
- Absolute paths used on the server-side for SSR compatibility

**Specific Route Mapping:**
- Frontend `/api/auth/token` → Backend `/auth/api/auth/token` (after fixing double prefix)
- Frontend `/api/v1/chat/conversations` → Backend `/api/v1/chat/conversations` (after fixing double prefix)
- All other API routes follow the same pattern

**Environment Configuration:**
- NEXT_PUBLIC_BACKEND_API_URL set to empty string for client-side relative paths
- Server-side uses Kubernetes service names for internal communication
- Proper CORS configuration to allow frontend-originated requests

## Consequences

**Positive:**
- Proper separation of concerns between frontend and backend
- Seamless communication through Next.js proxy layer
- Maintains authentication and session handling
- Works correctly in both SSR and client-side rendering
- Resolves the double-prefix issue in API routes

**Negative:**
- Slightly more complex configuration than direct API calls
- Requires understanding of Next.js rewrite mechanics
- Additional network hop through Next.js proxy (minimal performance impact)

## Alternatives Considered

**Alternative 1: Direct Service-to-Service Communication**
- Frontend would make requests directly to backend service
- Simpler architecture but breaks browser CORS policies
- Rejected because browsers cannot directly access internal Kubernetes services

**Alternative 2: API Gateway Pattern**
- Introduce a dedicated API gateway service
- More complex but scalable for larger applications
- Rejected as over-engineering for this application size

**Alternative 3: Backend-for-Frontend (BFF) Pattern**
- Create a dedicated service to aggregate backend APIs
- Would add another service to maintain
- Rejected as unnecessary complexity for this use case

## References
- `/frontend/next.config.ts` - Next.js rewrite configuration
- `/frontend/src/lib/api-client.ts` - API client implementation
- `/frontend/src/lib/auth-client.ts` - Authentication client implementation
- `/backend/src/api/v1/chat.py` - Backend chat API routes
- `/backend/src/main.py` - Backend router mounting configuration