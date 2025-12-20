# Research: Better Auth Integration with FastAPI

## Decision

Implement authentication using JWT (JSON Web Token) tokens issued by Better Auth on the Next.js frontend and verified by FastAPI on the backend.

## Rationale

The "Better Auth" library is primarily a JavaScript/TypeScript authentication library, making direct integration with a Python-based FastAPI backend infeasible. The proposed solution leverages JWT tokens as a bridge between the frontend and backend authentication mechanisms. This approach offers several benefits:

-   **User Isolation**: Ensures each user only accesses their own data.
-   **Stateless Authentication**: The backend can verify user authenticity without maintaining session state, improving scalability.
-   **Token Expiry**: JWTs can be configured to expire automatically, enhancing security.
-   **Independent Verification**: Both frontend and backend can independently verify authentication using a shared secret.
-   **Alignment with Project Requirements**: This method allows adherence to the "Better Auth" requirement while maintaining the FastAPI backend.

## Alternatives Considered

-   **Switching Backend Technology to Node.js**: This was considered but rejected due to the existing project constraint of using FastAPI for the backend.
-   **Using a Different Python Authentication Library for FastAPI**: This was rejected because the project explicitly specifies "Better Auth" as the authentication solution.
-   **Proceeding Without Authentication**: This was rejected as authentication is a fundamental requirement for a multi-user web application.

## Key Integration Steps

Based on the provided information, the integration will involve the following changes:

1.  **Better Auth Configuration (Frontend)**:
    *   Enable the JWT plugin within Better Auth to issue JWT tokens upon user login.

2.  **Frontend API Client (Next.js)**:
    *   Modify the frontend API client to attach the issued JWT token to every API request header in the format `Authorization: Bearer <token>`.

3.  **FastAPI Backend Middleware**:
    *   Implement a middleware in the FastAPI backend to intercept incoming requests.
    *   This middleware will extract the JWT token from the `Authorization` header.
    *   It will then verify the token's signature using a shared secret key.
    *   Upon successful verification, the middleware will extract user information (e.g., user ID, email) from the token and make it available to the API routes.

4.  **FastAPI API Routes**:
    *   All API routes will be updated to utilize the authenticated user's ID (obtained from the JWT token).
    *   Queries will be filtered to ensure that users can only access or modify their own tasks, enforcing task ownership.

5.  **Shared Secret Management**:
    *   A common secret key must be used by both the Better Auth configuration on the frontend and the FastAPI backend for JWT signing and verification.
    *   This secret will typically be managed via an environment variable, such as `BETTER_AUTH_SECRET`, in both services' `.env` files.

## API Behavior Change After Authentication

-   All API endpoints will require a valid JWT token.
-   Requests without a valid token will receive a `401 Unauthorized` response.
-   Each user will only be able to see and modify their own tasks, with task ownership enforced on every operation.
-   The REST API endpoints (e.g., `GET /api/user_id/tasks`, `POST /api/user_id/tasks`) will remain structurally similar, but every request will now include a JWT token, and all responses will be filtered to include only the authenticated user's data.
