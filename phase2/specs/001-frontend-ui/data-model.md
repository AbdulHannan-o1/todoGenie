# Data Model: Frontend UI/UX

## Entities

### User (Frontend Context)

This entity represents the user from the frontend's perspective, primarily for managing client-side preferences.

**Attributes**:

*   **id**: Unique identifier for the user (received from backend authentication).
*   **themePreference**: String, stores the user's chosen theme ('light' or 'dark'). This preference is stored locally (e.g., in browser local storage) and is associated with the authenticated user.

**Relationships**:

*   None directly within the frontend context, but implicitly linked to the backend's User entity via `id` after authentication.
