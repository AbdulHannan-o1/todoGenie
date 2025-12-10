# Todo Genie - Phase 2 Web Application

This repository contains the Phase 2 implementation of the Todo Genie application, a full-stack web application built with Next.js (frontend) and FastAPI (backend).

## Project Structure

-   `frontend/`: Next.js application
-   `backend/`: FastAPI application
-   `docker-compose.yml`: Docker Compose configuration for the PostgreSQL database.
-   `run-dev.sh`: Script to start the entire development environment.

## Getting Started

### Prerequisites

Ensure you have the following installed:

-   **Docker Desktop**: For running the PostgreSQL database.
-   **Python 3.10+**: For the FastAPI backend.
-   **Node.js 18+**: For the Next.js frontend.

### Setup and Run

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd todogenie/phase2
    ```

2.  **Start the development environment:**
    Use the provided `run-dev.sh` script to start both the PostgreSQL database, FastAPI backend, and Next.js frontend concurrently.

    ```bash
    chmod +x run-dev.sh
    ./run-dev.sh
    ```
    This script will:
    -   Start the PostgreSQL container using `docker compose`.
    -   Activate the Python virtual environment, install backend dependencies (if not already installed), and start the FastAPI server.
    -   Install frontend dependencies (if not already installed) and start the Next.js development server.

3.  **Access the applications:**
    -   **Frontend:** `http://localhost:3000`
    -   **Backend API (Swagger UI):** `http://localhost:8000/docs`

### Environment Variables

-   **Backend (`backend/.env`):**
    ```
    DATABASE_URL="postgresql://user:password@localhost:5432/todogenie_db"
    BETTER_AUTH_SECRET="YOUR_SUPER_SECRET_KEY_FOR_JWT" # IMPORTANT: Change this to a strong, random key
    ```
-   **Frontend (`frontend/.env.local`):**
    ```
    NEXT_PUBLIC_BACKEND_API_URL="http://localhost:8000"
    NEXT_PUBLIC_BETTER_AUTH_SECRET="YOUR_SUPER_SECRET_KEY_FOR_JWT" # IMPORTANT: Must match backend secret
    ```
    **Note**: Create these files from their `.example` counterparts and fill in the `BETTER_AUTH_SECRET` with a strong, random key. Ensure the secret is the same for both frontend and backend.

## API Interaction

You can interact with the API via the frontend application or directly through the Swagger UI:

1.  Go to `http://localhost:8000/docs`.
2.  Use the `/auth/register` endpoint to create a new user.
3.  Use the `/auth/login` endpoint to get an `access_token`.
4.  Authorize your requests in Swagger UI using the `access_token` (Bearer authentication).
5.  Now you can use the `/api/tasks` endpoints to create, view, update, and delete tasks for your authenticated user.
