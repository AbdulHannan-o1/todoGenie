# Tasks: Phase 2 Web Application Initialization

This document outlines the tasks required to initialize the full-stack web application for Phase 2 of the Todo Genie project.

## Phase 1: Project Setup

- [X] T001 Create the monorepo structure with `phase2/frontend` and `phase2/backend` directories.
- [X] T002 Initialize a `git` repository in the root directory.

## Phase 2: Foundational Setup

- [X] T003 [P] Create a `docker-compose.yml` file in the `phase2` directory to run a PostgreSQL container for the database.
- [X] T004 [P] Create a `.env.example` file in `phase2/backend` with placeholders for `DATABASE_URL` and `BETTER_AUTH_SECRET`.
- [X] T005 [P] Create a `.env.local.example` file in `phase2/frontend` with placeholders for `NEXT_PUBLIC_BACKEND_API_URL` and `NEXT_PUBLIC_BETTER_AUTH_SECRET`.

## Phase 3: User Story 1 - Initialize Frontend Application

- **Goal**: Set up and run the Next.js frontend application.
- **Independent Test**: The frontend application starts, and the default Next.js page is accessible in a web browser.

- [X] T006 [US1] Initialize a new Next.js 16 (use typescript) application with the App Router in the `phase2/frontend` directory.
- [X] T007 [US1] Install frontend dependencies: `tailwindcss`, `shadcn-ui`, and any other required packages in `phase2/frontend/package.json`.
- [X] T008 [US1] Configure Tailwind CSS in `phase2/frontend/tailwind.config.js` and `phase2/frontend/postcss.config.js`.
- [X] T009 [US1] Configure shadcn/ui by running its initialization command in the `phase2/frontend` directory.
- [X] T010 [US1] Create a basic layout component in `phase2/frontend/app/layout.tsx` that includes a header and a main content area.

## Phase 4: User Story 2 - Initialize Backend Application

- **Goal**: Set up and run the FastAPI backend application.
- **Independent Test**: The backend application starts, and the default FastAPI documentation is accessible at `/docs`.

- [X] T011 [US2] Initialize a new FastAPI application in `phase2/backend/main.py`.
- [X] T012 [US2] Create a `requirements.txt` file in `phase2/backend` and add backend dependencies: `fastapi`, `uvicorn`, `sqlmodel`, `psycopg2-binary`, `alembic`, `python-dotenv`, `python-jose[cryptography]`, `passlib[bcrypt]`.
- [X] T013 [US2] Implement database connection logic in `phase2/backend/db.py` to connect to the PostgreSQL database using `sqlmodel`.
- [X] T014 [US2] Create the `User` and `Task` models in `phase2/backend/models.py` as defined in `data-model.md`.
- [X] T015 [US2] Set up Alembic for database migrations in the `phase2/backend` directory.
- [X] T016 [US2] Generate an initial Alembic migration script for the `User` and `Task` models.
- [X] T017 [US2] Implement JWT authentication middleware in `phase2/backend/auth.py` to verify tokens and extract user information.
- [X] T018 [US2] Implement authentication routes (`/auth/register`, `/auth/login`) in `phase2/backend/routes/auth.py`.
- [X] T019 [US2] Implement task CRUD routes (`/api/tasks`) in `phase2/backend/routes/tasks.py`, ensuring they are protected by the JWT middleware.

## Phase 5: User Story 3 - Monorepo Structure

- **Goal**: Ensure a clear monorepo structure.
- **Independent Test**: The project directory contains `frontend` and `backend` subdirectories at the root of the `phase2` directory.

- [X] T020 [US3] Verify that the project structure in the `phase2` directory matches the monorepo standard defined in the plan.

## Phase 6: User Story 4 - Development Environment Script

- **Goal**: Create a single script to start the entire development environment.
- **Independent Test**: Running the script successfully starts both the frontend and backend applications.

- [X] T021 [US4] Create a `run-dev.sh` script in the `phase2` directory that starts both the frontend and backend development servers concurrently.

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T022 [P] Create a root-level `README.md` in the `phase2` directory with instructions on how to use the `run-dev.sh` script.
- [X] T023 [P] Implement structured (JSON) logging in the FastAPI backend for key events.
- [X] T024 [P] Implement basic security headers (CORS, XSS, etc.) in the FastAPI backend.

## Dependencies

- **User Story 1** and **User Story 2** can be implemented in parallel.
- **User Story 3** is a verification step that can be done at any time.
- **User Story 4** depends on the completion of User Story 1 and User Story 2.

## Parallel Execution Examples

- **Story 1 (Frontend)**:
  - `T006`, `T007`, `T008`, `T009`, `T010` can be executed sequentially.
- **Story 2 (Backend)**:
  - `T011`, `T012`, `T013`, `T014`, `T015`, `T016`, `T017`, `T018`, `T019` can be executed sequentially.

## Implementation Strategy

The implementation will follow an MVP-first approach. The initial focus will be on completing User Story 1 and User Story 2 to establish the core frontend and backend services. Once these are in place, the development environment script (User Story 4) will be created to streamline the development workflow.
