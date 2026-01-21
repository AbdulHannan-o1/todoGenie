# ADR 003: Resolving Double Prefix Issue in Backend API Routes

## Status
Accepted

## Date
2026-01-21

## Context
During the Kubernetes deployment, we discovered that the backend API routes had a double prefix issue. The chat API routes were appearing as `/api/v1/chat/api/v1/chat/conversations` instead of the expected `/api/v1/chat/conversations`. This caused frontend API calls to fail with 404 errors.

## Decision
We decided to fix the double prefix issue by removing the redundant prefix from the router definition in the backend code:

**Original Code:**
```python
# In src/api/v1/chat.py
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

**Fixed Code:**
```python
# In src/api/v1/chat.py
router = APIRouter(tags=["chat"])
```

The prefix is still applied at the mounting level in `src/main.py`:
```python
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
```

This ensures that the final route becomes `/api/v1/chat/conversations` instead of `/api/v1/chat/api/v1/chat/conversations`.

## Consequences

**Positive:**
- API routes are now correctly formatted without duplication
- Frontend can successfully call backend API endpoints
- Consistent with expected API contract
- Eliminates confusion in API documentation and client implementations

**Negative:**
- Required rebuilding and redeploying the backend Docker image
- Minor code change required in the backend service

## Alternatives Considered

**Alternative 1: Fix in Next.js Rewrites Only**
- Modify frontend proxy configuration to handle the double-prefixed paths
- Rejected because it would mask the underlying issue and create inconsistent API contracts

**Alternative 2: Keep Both Prefixes and Update All References**
- Update frontend to call the double-prefixed endpoints
- Rejected because it would create unnecessarily complex and confusing API paths

**Alternative 3: Create API Gateway Layer**
- Introduce a reverse proxy to remap paths
- Rejected as over-engineering for this issue

## References
- `/backend/src/api/v1/chat.py` - Fixed router definition
- `/backend/src/main.py` - Router mounting configuration
- `/frontend/next.config.ts` - Next.js rewrite configuration
- Issue discovered during testing of chat functionality
- OpenAPI spec verification confirmed the fix