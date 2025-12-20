# Quickstart Guide: Phase 2 Web Application Initialization

This guide provides instructions for setting up and running the Todo Genie full-stack web application development environment.

## 1. Prerequisites

Ensure you have the following installed on your system:

-   **Python 3.10+**: For the FastAPI backend.
-   **Node.js 18+**: For the Next.js frontend.
-   **npm** or **yarn**: Node.js package managers.
-   **Docker Desktop**: Recommended for running a local PostgreSQL database.
-   **Git**: For cloning the repository.

## 2. Clone the Repository

First, clone the Todo Genie repository to your local machine:

```bash
git clone <repository-url>
cd todogenie/phase2
```

## 3. Backend Setup (FastAPI)

Navigate to the `backend` directory within `phase2`:

```bash
cd backend
```

### 3.1. Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: `requirements.txt` will be generated during implementation, for now, assume it exists or install `fastapi`, `uvicorn`, `sqlmodel`, `psycopg2-binary`, `alembic`, `python-dotenv`, `python-jose[cryptography]`, `passlib[bcrypt]` manually)*

### 3.2. Database Setup (PostgreSQL with Docker)

It is recommended to run a local PostgreSQL instance using Docker.

```bash
# Create a Docker network for the application (if not already exists)
docker network create todogenie-network || true

# Run PostgreSQL container
docker run --name todogenie-postgres \
    --network todogenie-network \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=todogenie_db \
    -p 5432:5432 \
    -d postgres:15
```

### 3.3. Environment Variables

Create a `.env` file in the `backend` directory with the following content:

```
DATABASE_URL="postgresql://user:password@localhost:5432/todogenie_db"
BETTER_AUTH_SECRET="YOUR_SUPER_SECRET_KEY_FOR_JWT" # IMPORTANT: Change this to a strong, random key
```
**Note**: The `BETTER_AUTH_SECRET` must be the same as configured in the frontend's Better Auth setup.

### 3.4. Run Database Migrations

```bash
alembic upgrade head
```
*(Note: Alembic setup and initial migrations will be part of the backend implementation)*

### 3.5. Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```
The backend API will be accessible at `http://localhost:8000`. The API documentation (Swagger UI) will be at `http://localhost:8000/docs`.

## 4. Frontend Setup (Next.js)

Open a new terminal and navigate to the `frontend` directory within `phase2`:

```bash
cd ../frontend
```

### 4.1. Install Dependencies

```bash
npm install # or yarn install
```

### 4.2. Environment Variables

Create a `.env.local` file in the `frontend` directory with the following content:

```
NEXT_PUBLIC_BACKEND_API_URL="http://localhost:8000"
NEXT_PUBLIC_BETTER_AUTH_SECRET="YOUR_SUPER_SECRET_KEY_FOR_JWT" # IMPORTANT: Must match backend secret
```
**Note**: The `NEXT_PUBLIC_BETTER_AUTH_SECRET` must be the same as configured in the backend.

### 4.3. Start the Frontend Development Server

```bash
npm run dev # or yarn dev
```
The frontend application will be accessible at `http://localhost:3000`.

## 5. Basic Usage

Once both the frontend and backend servers are running:

1.  Open your web browser and navigate to `http://localhost:3000`.
2.  You should see the Next.js welcome page or the initial Todo Genie application interface.
3.  You can interact with the backend API through the frontend application.
4.  To test API endpoints directly, you can use tools like Postman, Insomnia, or the Swagger UI at `http://localhost:8000/docs`.

### Example API Interaction (via Swagger UI)

1.  Go to `http://localhost:8000/docs`.
2.  Use the `/auth/register` endpoint to create a new user.
3.  Use the `/auth/login` endpoint to get an `access_token`.
4.  Authorize your requests in Swagger UI using the `access_token` (Bearer authentication).
5.  Now you can use the `/api/tasks` endpoints to create, view, update, and delete tasks for your authenticated user.
