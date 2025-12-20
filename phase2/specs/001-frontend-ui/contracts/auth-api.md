# API Contracts: Authentication

This document outlines the expected API interactions for user authentication, which the frontend UI/UX will consume. These endpoints are assumed to be provided by the `Better Auth` backend integration.

## 1. User Registration

**Endpoint**: `/api/auth/register`
**Method**: `POST`
**Description**: Registers a new user account.
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response (Success - 201 Created)**:
```json
{
  "message": "User registered successfully",
  "user_id": "uuid-of-new-user"
}
```
**Response (Error - 400 Bad Request)**:
```json
{
  "detail": "Email already registered"
}
```

## 2. User Login

**Endpoint**: `/api/auth/login`
**Method**: `POST`
**Description**: Authenticates a user and provides access tokens.
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response (Success - 200 OK)**:
```json
{
  "access_token": "jwt-access-token",
  "token_type": "bearer"
}
```
**Response (Error - 401 Unauthorized)**:
```json
{
  "detail": "Invalid credentials"
}
```

## 3. User Logout

**Endpoint**: `/api/auth/logout`
**Method**: `POST`
**Description**: Invalidates the user's session/token.
**Request Headers**:
```
Authorization: Bearer jwt-access-token
```
**Response (Success - 200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```
**Response (Error - 401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

## 4. User Profile (Example - Requires Authentication)

**Endpoint**: `/api/users/me`
**Method**: `GET`
**Description**: Retrieves the authenticated user's profile information.
**Request Headers**:
```
Authorization: Bearer jwt-access-token
```
**Response (Success - 200 OK)**:
```json
{
  "user_id": "uuid-of-user",
  "email": "user@example.com",
  "name": "User Name",
  "theme_preference": "light" // Example of a user preference that might be stored on backend
}
```
**Response (Error - 401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```
