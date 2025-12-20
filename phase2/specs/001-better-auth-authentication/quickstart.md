# Quickstart: Better Auth Authentication

This guide provides a quick overview of how to get started with the Better Auth Authentication feature.

## 1. Setup Environment

Ensure your backend and frontend services are running. Refer to the main project's `README.md` for instructions on how to start the development servers.

**Environment Variables**:
Before running the backend, ensure the `ENCRYPTION_KEY` environment variable is set. You can generate a key using `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.

## 2. Register a New User

To register a new user, send a `POST` request to the `/users/register` endpoint with the user's email, username, and password.

**Request Example (cURL)**:

```bash
curl -X POST "http://localhost:8000/users/register" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "test@example.com",
           "username": "testuser",
           "password": "securepassword123"
         }'
```

**Expected Response (201 Created)**:

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "email": "test@example.com",
  "username": "testuser"
}
```

## 3. Log In and Obtain an Access Token

After registration, log in to obtain an access token. Send a `POST` request to the `/users/login` endpoint with either the user's email or username, and their password.

**Request Example (cURL)**:

```bash
curl -X POST "http://localhost:8000/users/login" \
     -H "Content-Type: application/json" \
     -d '{
           "identifier": "test@example.com",
           "password": "securepassword123"
         }'
```

**Expected Response (200 OK)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Note**: Store the `access_token` securely. It will be used for authenticating subsequent requests to protected endpoints.

## 4. Make an Authenticated Request (e.g., Get Tasks)

Use the obtained `access_token` in the `Authorization` header as a Bearer token to access protected resources, such as fetching tasks.

**Request Example (cURL)**:

```bash
curl -X GET "http://localhost:8000/tasks" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response (200 OK)**:

```json
[
  {
    "id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
    "content": "Buy groceries",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  },
  {
    "id": "g1h2i3j4-k5l6-7890-1234-567890abcdef",
    "content": "Walk the dog",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
]
```

## 5. Log Out

To invalidate the current session, send a `POST` request to the `/users/logout` endpoint with your access token.

**Request Example (cURL)**:

```bash
curl -X POST "http://localhost:8000/users/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response (200 OK)**:

```
(No content)
```
