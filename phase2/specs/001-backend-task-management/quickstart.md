# Quickstart Guide: Backend Task Management

This guide provides instructions to quickly set up and interact with the Backend Task Management API.

## Prerequisites

*   Python 3.10+
*   Docker and Docker Compose (for local database setup)
*   `pip` (Python package installer)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd todogenie
    ```

2.  **Navigate to the backend directory:**
    ```bash
    cd phase2/backend
    ```

3.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Copy the `.env.example` file to `.env` and update the values as needed.
    ```bash
    cp .env.example .env
    # Edit .env to configure your database connection and other settings
    ```

5.  **Start the database (using Docker Compose):**
    Navigate to the `phase2` directory and start the database.
    ```bash
    cd ../.. # Go back to the todogenie/phase2 directory
    docker-compose up -d db
    ```

6.  **Run database migrations:**
    Navigate back to the `backend` directory and run Alembic migrations.
    ```bash
    cd backend
    alembic upgrade head
    ```

7.  **Start the FastAPI application:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

## API Interaction

You can interact with the API using tools like `curl`, Postman, or by accessing the interactive OpenAPI documentation (Swagger UI).

### Accessing Swagger UI

Once the FastAPI application is running, open your web browser and navigate to:
`http://127.0.0.1:8000/docs`

Here you can explore all available endpoints, their request/response schemas, and even test them directly.

### Example `curl` Commands

**1. Register a User (assuming an authentication endpoint exists):**
*(Note: This endpoint is assumed based on authentication requirements and needs to be implemented.)*
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d 
     {
           "username": "testuser",
           "email": "test@example.com",
           "password": "securepassword"
         }
```

**2. Login and Get a JWT Token:**
*(Note: This endpoint is assumed based on authentication requirements and needs to be implemented.)*
```bash
curl -X POST "http://127.00.1:8000/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=securepassword"
# Save the "access_token" from the response for subsequent requests.
```

**3. Create a Task:**
Replace `<YOUR_JWT_TOKEN>` with the token obtained from login.
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d 
     {
           "title": "Buy groceries",
           "description": "Milk, eggs, bread, vegetables",
           "priority": "high",
           "due_date": "2025-12-15T18:00:00Z"
         }
```

**4. List Tasks:**
```bash
curl -X GET "http://127.0.0.1:8000/tasks" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

**5. Mark Task as Complete:**
Replace `<TASK_ID>` with an actual task ID.
```bash
curl -X PATCH "http://127.0.0.1:8000/tasks/<TASK_ID>/complete" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

## Next Steps

*   Implement the authentication endpoints (`/auth/register`, `/auth/token`).
*   Implement the task management endpoints as defined in the OpenAPI specification.
*   Integrate WhatsApp notification functionality.
*   Set up the cron worker for recurring tasks and reminders.
