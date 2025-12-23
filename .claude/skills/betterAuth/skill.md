# Better Auth Integration Skill

## Overview
This skill provides comprehensive guidance for implementing Better Auth with the TodoGenie FastAPI backend. It covers the hybrid authentication approach that maintains JWT compatibility while integrating Better Auth into the Next.js frontend.

## Implementation Approach

### Hybrid Authentication Architecture
The TodoGenie project implements a hybrid authentication approach that combines:
- **Frontend**: Next.js application with Better Auth client integration
- **Backend**: FastAPI application with JWT token validation
- **Shared Secret**: BETTER_AUTH_SECRET for token signing/verification

### Integration Strategy
The current implementation follows these key principles:
1. Better Auth is installed in the frontend but uses existing FastAPI backend for user validation
2. JWT tokens are generated using the shared BETTER_AUTH_SECRET
3. Frontend API calls automatically include JWT tokens in Authorization headers
4. Backend validates tokens using the same secret and enforces user isolation

## Token Compatibility Research

### JWT Algorithm Compatibility
- Both systems use HS256 algorithm for token signing
- Shared secret (BETTER_AUTH_SECRET) ensures cross-system token validation
- Token payload structure is compatible between systems:
  - User ID stored in "sub" claim
  - Additional claims maintained for backend compatibility

### Compatibility Requirements
1. Same signing algorithm (HS256) used by both systems
2. Identical secret (BETTER_AUTH_SECRET) for token generation/validation
3. Compatible token payload structure with required claims
4. Proper token expiration handling across both systems

## Hybrid Authentication Implementation

### Frontend Implementation
- Better Auth client library installed and configured
- Authentication context manages user sessions and tokens
- API client automatically injects JWT tokens with requests
- Login/Signup pages integrated with the auth system

### Backend Implementation
- JWT token validation using BETTER_AUTH_SECRET
- User isolation enforced on all endpoints
- Task ownership verification on CRUD operations
- FastAPI security dependencies for authentication

### Token Flow
1. User registers/logs in through frontend forms
2. Credentials are sent to FastAPI backend for validation
3. Backend creates JWT token using BETTER_AUTH_SECRET
4. Token is stored in localStorage and sent with subsequent requests
5. Backend validates tokens on protected endpoints
6. User data is retrieved from token payload

## Key Implementation Details

### Environment Configuration
**Frontend (.env.local):**
```
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

**Backend (.env):**
```
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

### Core Files Modified
1. `src/context/auth-context.tsx` - Authentication context with Better Auth patterns
2. `src/lib/auth-client.ts` - Auth client for Better Auth compatibility
3. `src/lib/api-client.ts` - JWT token handling and error management
4. `src/app/login/page.tsx` - Updated login page with new auth methods
5. `src/app/signup/page.tsx` - Updated signup page with new auth methods
6. `src/lib/better-auth-client.ts` - Better Auth client configuration
7. `src/config.py` - Backend configuration for JWT handling

### Security Considerations
- Tokens use HS256 algorithm with strong secret
- Proper token expiration implemented (7 days default)
- Secure token storage in localStorage
- All API requests require valid tokens
- User isolation enforced on all operations

## User Isolation and Task Ownership

### Database-Level Enforcement
- Foreign key constraints ensure task ownership
- User ID stored with each task record
- Queries automatically filtered by authenticated user

### API-Level Validation
- All protected endpoints validate user authentication
- Ownership verification on CRUD operations
- Cross-user data access prevented

### Implementation Example
```python
# In task endpoints
def get_user_tasks(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_tasks_by_user_id(session, user.id)
```

## Environment Variable Setup

### BETTER_AUTH_SECRET Configuration
The BETTER_AUTH_SECRET environment variable is critical for the authentication system:

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

**Backend (.env):**
```bash
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

### Secret Generation
To generate a secure secret:
```bash
openssl rand -base64 32
```

### Production Considerations
- Use strong, unique secrets in production
- Never commit secrets to version control
- Use environment-specific secrets for dev/staging/production
- Implement proper secret rotation procedures

## Troubleshooting Tips

### Token Validation Issues
**Symptoms:** 401 Unauthorized errors, token validation failures
**Solutions:**
- Verify BETTER_AUTH_SECRET matches between frontend and backend
- Check JWT algorithm consistency (HS256)
- Validate token format and structure
- Ensure proper token storage/retrieval in localStorage

### Authentication Flow Issues
**Symptoms:** Login failures, registration issues, session problems
**Solutions:**
- Check API endpoint availability and CORS configuration
- Verify proper token storage and retrieval
- Confirm API client is correctly configured
- Check network connectivity to backend services

### User Isolation Problems
**Symptoms:** Users seeing other users' data, ownership validation failures
**Solutions:**
- Validate user ID extraction from JWT tokens
- Check ownership verification logic in API endpoints
- Ensure proper user context in requests
- Verify database foreign key constraints

### Common Error Scenarios
1. **Environment Mismatch:** Ensure secrets match across frontend and backend
2. **CORS Issues:** Configure proper CORS settings for API communication
3. **Token Expiration:** Implement proper token refresh mechanisms
4. **Session Management:** Handle token expiration gracefully with re-authentication

### Debugging Steps
1. Check environment variables are properly set
2. Verify API endpoints are accessible
3. Test token generation and validation independently
4. Review authentication flow in browser developer tools
5. Check backend logs for authentication-related errors

## Future Improvements

### Full Better Auth Integration Options
1. **Next.js Auth API Routes:** Implement Better Auth in Next.js API routes as authentication proxy
2. **Backend Migration:** Migrate FastAPI auth to use Better Auth patterns while maintaining JWT compatibility
3. **Separate Auth Service:** Create dedicated authentication service using Better Auth

### Security Enhancements
- Implement token refresh mechanisms
- Add MFA support
- Enhance session management
- Implement CSRF protection

## Testing Checklist

### Authentication Flow Testing
- [ ] User registration with email/password
- [ ] User login with valid credentials
- [ ] Token storage and retrieval
- [ ] API requests with valid tokens
- [ ] Logout functionality
- [ ] Token expiration handling
- [ ] Error handling for invalid credentials

### User Isolation Testing
- [ ] Users can only see their own tasks
- [ ] Cross-user data access prevented
- [ ] Proper ownership verification on all operations
- [ ] Database constraints properly enforced