# TodoGenie Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### I. Spec-First Design
<!-- Example: I. Library-First -->
All features must start with a formal specification; no implementation without a clear blueprint. Specs must include API contracts, data models, system behavior, error handling, and acceptance criteria. This ensures maintainable, AI-driven, spec-compliant development.

### II. Test-Driven Development (TDD)
For any new feature or bug fix, tests that verify the functionality must be written first. These tests will initially fail (Red). Implementation code must then be written with the sole purpose of making these tests pass (Green). Once passing, the code can be refactored for clarity and efficiency while ensuring tests continue to pass.

### III. Web-First API Interface
<!-- Example: II. CLI Interface -->
The application is a full-stack web application with a strict separation between the frontend (Next.js) and backend (FastAPI). All communication must occur over a stateless, RESTful API.

### IV. Persistent Database Storage (NON-NEGOTIABLE)
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
All application data must be persisted in a Neon Serverless PostgreSQL database. Data must be durable and survive application restarts. All database interactions from the backend must be managed via the SQLModel ORM.

### V. RESTful CRUD and AI-Driven Enhancements
<!-- Example: IV. Integration Testing -->
Core functionality is exposed via RESTful CRUD API endpoints (Create, Read, Update, Delete). AI-driven features include: Auto-categorization, Deadline suggestions, Task title improvements, Natural language processing for task creation, and Voice-to-task conversion.

### VI. Full-Stack Monorepo Architecture
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
The project follows a monorepo architecture with distinct frontend and backend services. `/frontend` contains the Next.js application, and `/backend` contains the FastAPI application. This separation enforces a clean client-server model and allows for independent development and deployment.

### VII. Observability & User Feedback
The API must provide clear success and error responses using standard HTTP status codes. The frontend will translate these responses into user-friendly feedback. All operations must be logged for traceability and debugging.

### VIII. AI Integration & Natural Language Processing
The application incorporates AI-driven features that allow users to interact with the system through natural language and voice commands. This includes AI chatbot functionality, voice processing, and intelligent task management capabilities.

### IX. Automated Task Management & Reminders
The system includes automated task management features including overdue task detection, reminder scheduling, and recurring task functionality. A background job scheduler monitors tasks and sends notifications for upcoming and overdue tasks.

## Additional Constraints
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->
- **Frontend:** Next.js 16+, TypeScript, Tailwind CSS, Shadcn UI
- **Backend:** Python 3.10+, FastAPI, SQLModel ORM
- **Database:** Neon Serverless PostgreSQL with SQLModel ORM
- **Authentication:** Multi-user support with Better Auth, using JWTs to secure API endpoints.
- **Spec-Driven:** Claude Code + Spec-Kit Plus
- **AI Integration:** OpenAI-compatible API for natural language processing and voice-to-text conversion
- **Task Management:** Overdue task detection, reminder scheduling, and recurring task functionality
- All API requests must be authenticated, and data access must be strictly scoped to the authenticated user.
- Background job processing for automated task reminders and overdue notifications

## Development Workflow
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->
- **Spec-Driven:** Implementations must strictly follow the constitution and its referenced specifications.
- **Test-Driven Development (TDD):** All new functionality or bug fixes must begin with writing failing tests (Red). Implementation code is then written to make the tests pass (Green), followed by optional code cleanup (Refactor). This applies to backend (pytest) and frontend tests.
- **Code Review:** All code is reviewed for spec compliance, security, maintainability, and adherence to the TDD process.
- **Documentation:** Every module must include comments describing its purpose and behavior.
- **Error Handling:** The API must handle all errors gracefully, returning informative JSON error messages.
- **AI Integration Testing:** All AI-driven features must be thoroughly tested with both positive and negative scenarios.

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->
The constitution supersedes all other coding practices. Any amendment must be documented, approved, and a migration plan provided. All PRs and reviews must verify spec compliance. Complexity must be justified. Specs are the single source of truth for runtime behavior.

**Version**: 3.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-24
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->