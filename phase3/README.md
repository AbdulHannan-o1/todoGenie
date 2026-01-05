# Todo Genie - Phase 3 AI Chatbot with Voice Support

This repository contains the Phase 3 implementation of the Todo Genie application, a full-stack web application with AI Chatbot and Voice Support built with Next.js (frontend), FastAPI (backend), and MCP (Model Context Protocol) server, featuring better-auth for authentication.

## Project Structure

-   `frontend/`: Next.js application
-   `backend/`: FastAPI application with MCP (Model Context Protocol) server
-   `docker-compose.yml`: Docker Compose configuration for the PostgreSQL database.
-   `run-dev.sh`: Script to start the entire development environment.

## Getting Started

### Prerequisites

Ensure you have the following installed:

-   **Docker Desktop**: For running the PostgreSQL database.
-   **Python 3.10+**: For the FastAPI backend and MCP server.
-   **Node.js 18+**: For the Next.js frontend.

### Setup and Run

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd todogenie/phase3
    ```

2.  **Set up environment variables:**
    Create the necessary environment files from their examples:

    ```bash
    # Backend environment
    cd backend
    cp .env.example .env
    # Edit .env to add your BETTER_AUTH_SECRET and database configuration
    cd ..

    # Frontend environment
    cd frontend
    echo "NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000" > .env.local
    # Add any frontend-specific environment variables if needed
    cd ..
    ```

3.  **Start the development environment:**
    Use the provided `run-dev.sh` script to start the PostgreSQL database, FastAPI backend with MCP server, and Next.js frontend concurrently.

    ```bash
    chmod +x run-dev.sh
    ./run-dev.sh
    ```
    This script will:
    -   Start the PostgreSQL container using `docker compose`.
    -   Activate the Python virtual environment, install backend dependencies (if not already installed), and start the FastAPI server with the integrated MCP server.
    -   Install frontend dependencies (if not already installed) and start the Next.js development server.

4.  **Access the applications:**
    -   **Frontend:** `http://localhost:3000`
    -   **Backend API (Swagger UI):** `http://localhost:8000/docs`
    -   **MCP Server:** Runs integrated within the FastAPI backend on port 8000

5.  **Manual Server Startup (Alternative):**
    If you prefer to start servers individually:

    **Start Backend (with MCP server):**
    ```bash
    cd backend
    source .venv/bin/activate  # or your virtual environment activation command
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

    **Start Frontend:**
    ```bash
    cd frontend
    npm run dev
    ```

    **Note:** The MCP (Model Context Protocol) server starts automatically when the main FastAPI application starts, as it's integrated into the backend.

### Environment Variables

-   **Backend (`backend/.env`):**
    ```
    DATABASE_URL="postgresql://neondb_owner:your_password@ep-purple-tree-a437kbcj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    BETTER_AUTH_SECRET="your-better-auth-secret-here"
    ```
-   **Frontend (`frontend/.env.local`):**
    ```
    NEXT_PUBLIC_BACKEND_API_URL="http://localhost:8000"
    ```
    **Note**: The BETTER_AUTH_SECRET must be the same in both frontend and backend for proper JWT authentication. For local development with Neon PostgreSQL, update the DATABASE_URL with your actual Neon database credentials.

## Features

- **Authentication**: Secure user registration and login using better-auth with JWT tokens
- **Task Management**: Create, read, update, and delete personal tasks
- **AI Chatbot**: Conversational interface using OpenAI Agents SDK to manage tasks via natural language
- **Voice Support**: Voice input and output capabilities for hands-free task management
- **Responsive UI**: Modern UI built with Next.js and Tailwind CSS
- **API Documentation**: Interactive API documentation available at `/docs`
- **MCP Integration**: Model Context Protocol server for AI tool integration

## API Interaction

You can interact with the API via the frontend application or directly through the Swagger UI:

1. Go to `http://localhost:8000/docs`.
2. Use the `/auth/register` endpoint to create a new user.
3. Use the `/auth/token` endpoint to get an `access_token` (using OAuth2 password flow).
4. Authorize your requests in Swagger UI using the `access_token` (Bearer authentication).
5. Now you can use the `/api/tasks` endpoints to create, view, update, and delete tasks for your authenticated user.

## AI Chatbot and MCP Integration

The application features an AI Chatbot with voice support integrated via the MCP (Model Context Protocol) server:

- **Chat Interface**: Available through the frontend at `/chat`
- **MCP Tools**: The backend exposes MCP tools for AI agents to interact with task management functionality
- **Voice Commands**: Speak naturally to create, update, and manage tasks using the voice interface

## Database Configuration

The application uses Neon PostgreSQL for the database. For local development:
1. Create a free Neon account at https://neon.tech
2. Create a new project
3. Copy the connection string from the Project Dashboard > Connection Details
4. Update the `DATABASE_URL` in your `backend/.env` file
5. The application will automatically create required tables on startup

## Development

For development, the application uses:
- FastAPI with automatic API documentation (Swagger UI)
- Next.js 16 with TypeScript
- Tailwind CSS for styling
- Better-auth for authentication
- PostgreSQL database with Neon 