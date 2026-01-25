# Better Auth Integration Guide

This document explains how to properly integrate Better Auth with the existing FastAPI backend.

## Current Architecture

The current architecture consists of:
- Frontend: Next.js application
- Backend: FastAPI application with JWT authentication
- Shared secret: BETTER_AUTH_SECRET (used for JWT token signing/verification)

## Better Auth Integration Approach

Better Auth is primarily a Next.js/React authentication solution and doesn't have native Python/FastAPI support. To properly integrate Better Auth with this FastAPI backend, you have two main approaches:

### Approach 1: Next.js Auth API Routes (Recommended)

1. Set up Better Auth in the Next.js application using API routes
2. Use Next.js as the authentication layer
3. Have Better Auth issue JWT tokens compatible with the existing FastAPI backend
4. Update the FastAPI backend to accept tokens from Better Auth

#### Implementation Steps:

1. Create Next.js API routes for authentication:

```typescript
// pages/api/auth/[...nextauth].ts (or using the new app router approach)
import { NextApiHandler } from 'next';
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { verifyPassword } from '../../../lib/auth'; // Your existing auth logic
import { getUserByEmail } from '../../../lib/user'; // Your existing user logic

const handler: NextApiHandler = (req, res) => {
  return NextAuth(req, res, {
    providers: [
      CredentialsProvider({
        name: 'Credentials',
        credentials: {
          email: { label: 'Email', type: 'text' },
          password: { label: 'Password', type: 'password' }
        },
        async authorize(credentials) {
          if (!credentials?.email || !credentials?.password) {
            return null;
          }

          const user = await getUserByEmail(credentials.email);
          if (!user || !await verifyPassword(credentials.password, user.hashedPassword)) {
            return null;
          }

          return { id: user.id, email: user.email, name: user.name };
        }
      })
    ],
    secret: process.env.BETTER_AUTH_SECRET,
    jwt: {
      secret: process.env.BETTER_AUTH_SECRET,
    },
    callbacks: {
      async jwt({ token, user }) {
        if (user) {
          token.id = user.id;
        }
        return token;
      },
      async session({ session, token }) {
        if (token && token.id) {
          session.user.id = token.id as string;
        }
        return session;
      }
    }
  });
};

export default handler;
```

2. Update the FastAPI backend to accept Better Auth JWT tokens:

```python
# In your FastAPI auth module
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, settings.BETTER_AUTH_SECRET, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Approach 2: Hybrid Authentication (Current Implementation)

The current implementation in this project follows a hybrid approach:

1. Better Auth is installed in the frontend (though not fully configured)
2. The existing FastAPI JWT authentication system remains in place
3. Frontend authentication flow is managed through the AuthContext
4. JWT tokens are stored in localStorage and sent with API requests
5. The same BETTER_AUTH_SECRET is used for token signing/verification

This approach maintains compatibility while preparing for full Better Auth integration.

### Approach 3: Separate Authentication Service

Create a separate Next.js authentication service that uses Better Auth and acts as a proxy between the frontend and FastAPI backend:

1. Frontend communicates with Next.js auth service for login/register
2. Next.js auth service validates credentials against FastAPI backend
3. Next.js auth service issues Better Auth compatible JWT tokens
4. Frontend uses these tokens to communicate with FastAPI backend

## Configuration

### Environment Variables

Make sure the following environment variables are set:

Frontend (.env.local):
```
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
```

Backend (.env):
```
BETTER_AUTH_SECRET=your-secret-key-here
```

The same secret should be used for both Better Auth and FastAPI JWT token generation/validation.

## Token Compatibility

For Better Auth tokens to work with the existing FastAPI backend:

1. Both systems must use the same signing algorithm (HS256)
2. Both systems must use the same secret (BETTER_AUTH_SECRET)
3. Token payload structure should be compatible:
   - Include user ID in the "sub" claim
   - Include any additional claims needed by the backend

## Security Considerations

1. Ensure the BETTER_AUTH_SECRET is strong and kept secure
2. Use HTTPS in production to prevent token interception
3. Implement proper token expiration and refresh mechanisms
4. Validate tokens on every authenticated request
5. Implement proper CSRF protection

## Future Improvements

1. Complete the Better Auth backend configuration
2. Implement token refresh functionality
3. Add social authentication providers
4. Implement proper session management
5. Add MFA support if needed

## Troubleshooting

### Token Validation Issues
- Verify that both systems use the same secret
- Check that both systems use the same algorithm
- Ensure token format is compatible between systems

### Authentication Flow Issues
- Verify API endpoints are correctly configured
- Check that tokens are properly stored and sent with requests
- Ensure proper error handling throughout the auth flow