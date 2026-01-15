---
id: 0001
title: Create Database and Models Specification
stage: spec
date: 2025-12-11
surface: agent
model: gemini-1.5-flash-latest
feature: 001-db-models
branch: 001-db-models
user: abdulhannan
command: /sp.specify SPEC 2 — Database & Models (SQLModel + Neon PostgreSQL) 1. Purpose Define the complete data layer for Phase 2 of the Todo App. This includes: Task model with all fields needed for core, intermediate, and advanced features. Optional Tag model. Database connection setup. Session handling. Migration strategy. This spec ensures that all features (CRUD, search, filters, sorting, recurring tasks, due dates, reminders) are supported structurally. 2. Task Model Specification Task Model Fields Field Type Description id int (PK) Unique identifier user_id int (FK) Links task to the authenticated user title str Task name; required description Optional[str] Additional details completed bool = False Completion state priority enum("low", "medium", "high") Task priority level tags List[str] One or more labels (work, home, urgent) due_date Optional[datetime] Deadline for the task recurrence Optional[str] Values: daily, weekly, monthly created_at datetime Auto timestamp updated_at datetime Auto timestamp Recurrence Field Behavior If set, the system should regenerate a new task instance once the current one is completed or past due_date. 3. Tag Model Specification (Optional) Tag Model (only if using a separate table): id: int name: str user_id: int (FK) Pivot Table (TaskTag): task_id tag_id If tags remain inline (List[str]), this section can be skipped. 4. SQLModel Implementation Requirements Use SQLModel for ORM + schema models. Create separate models for: Task (DB model) TaskCreate (input schema) TaskUpdate (partial update schema) TaskRead (response schema) Enable automatic timestamp update via event listeners or default factories. 5. Database Setup (Neon PostgreSQL) Requirements Use Neon Serverless PostgreSQL. Store connection URL in .env as: DATABASE_URL=postgresql+psycopg://<user>:<pass>@<host>/<db> Engine Configuration Create engine with connection pooling: engine = create_engine(DATABASE_URL, echo=True) Session Handling Use dependency-based session injection: with Session(engine) as session: yield session 6. Migration Strategy Requirements Use Alembic + SQLModel migration pattern. Setup auto-generation of migrations. Use alembic.ini + env.py configured for SQLModel. Migrations to include Create tasks table Add tags column or join table Add recurrence column Add user_id foreign key 7. Constraints & Validation Rules title cannot be empty. priority must be one of: low, medium, high. recurrence must be: daily, weekly, monthly, or null. due_date must be a future date when provided. user_id links tasks to owners. 8. How This Supports All Features Basic Level Add / Delete / Update / View / Complete → uses basic fields. Intermediate Level Priority → priority Tags → tags or Tag table Search → title, description Filter → completed, priority, tags, due_date Sort → priority, due_date, title, created_at Advanced Level Recurring Tasks → recurrence Due Dates → due_date Reminders → due_date, timestamps 9. Deliverables /backend/models/task.py /backend/db/session.py /backend/db/engine.py /backend/migrations/ All fields and decisions here must be implemented exactly before writing backend routes.
labels: ["spec", "database", "models", "sqlmodel", "neon-postgresql"]
links:
  spec: specs/001-db-models/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-db-models/spec.md
  - specs/001-db-models/checklists/requirements.md
tests:

---

## Prompt

SPEC 2 — Database & Models (SQLModel + Neon PostgreSQL) 1. Purpose Define the complete data layer for Phase 2 of the Todo App. This includes: Task model with all fields needed for core, intermediate, and advanced features. Optional Tag model. Database connection setup. Session handling. Migration strategy. This spec ensures that all features (CRUD, search, filters, sorting, recurring tasks, due dates, reminders) are supported structurally. 2. Task Model Specification Task Model Fields Field Type Description id int (PK) Unique identifier user_id int (FK) Links task to the authenticated user title str Task name; required description Optional[str] Additional details completed bool = False Completion state priority enum("low", "medium", "high") Task priority level tags List[str] One or more labels (work, home, urgent) due_date Optional[datetime] Deadline for the task recurrence Optional[str] Values: daily, weekly, monthly created_at datetime Auto timestamp updated_at datetime Auto timestamp Recurrence Field Behavior If set, the system should regenerate a new task instance once the current one is completed or past due_date. 3. Tag Model Specification (Optional) Tag Model (only if using a separate table): id: int name: str user_id: int (FK) Pivot Table (TaskTag): task_id tag_id If tags remain inline (List[str]), this section can be skipped. 4. SQLModel Implementation Requirements Use SQLModel for ORM + schema models. Create separate models for: Task (DB model) TaskCreate (input schema) TaskUpdate (partial update schema) TaskRead (response schema) Enable automatic timestamp update via event listeners or default factories. 5. Database Setup (Neon PostgreSQL) Requirements Use Neon Serverless PostgreSQL. Store connection URL in .env as: DATABASE_URL=postgresql+psycopg://<user>:<pass>@<host>/<db> Engine Configuration Create engine with connection pooling: engine = create_engine(DATABASE_URL, echo=True) Session Handling Use dependency-based session injection: with Session(engine) as session: yield session 6. Migration Strategy Requirements Use Alembic + SQLModel migration pattern. Setup auto-generation of migrations. Use alembic.ini + env.py configured for SQLModel. Migrations to include Create tasks table Add tags column or join table Add recurrence column Add user_id foreign key 7. Constraints & Validation Rules title cannot be empty. priority must be one of: low, medium, high. recurrence must be: daily, weekly, monthly, or null. due_date must be a future date when provided. user_id links tasks to owners. 8. How This Supports All Features Basic Level Add / Delete / Update / View / Complete → uses basic fields. Intermediate Level Priority → priority Tags → tags or Tag table Search → title, description Filter → completed, priority, tags, due_date Sort → priority, due_date, title, created_at Advanced Level Recurring Tasks → recurrence Due Dates → due_date Reminders → due_date, timestamps 9. Deliverables /backend/models/task.py /backend/db/session.py /backend/db/engine.py /backend/migrations/ All fields and decisions here must be implemented exactly before writing backend routes.

## Response snapshot

The agent successfully created a new feature branch `001-db-models` and generated the `spec.md` file for "Database & Models (SQLModel + Neon PostgreSQL)". A quality checklist `requirements.md` was also created. The agent then validated the spec, identified a clarification regarding user deletion with associated tasks, and presented options to the user. Upon receiving the user's decision, the `spec.md` was updated to reflect the chosen behavior (reassign tasks to a deleted user data collection). The checklist was updated to reflect the resolution of the clarification.

## Outcome

- ✅ Impact: Created a detailed feature specification for the database and models, including user stories, functional requirements, and success criteria.
- 🧪 Tests: N/A
- 📁 Files: Created `specs/001-db-models/spec.md` and `specs/001-db-models/checklists/requirements.md`.
- 🔁 Next prompts: The feature is ready for `/sp.plan`.
- 🧠 Reflection: Successfully generated a technical specification from a detailed prompt, handled a clarification, and updated the spec accordingly.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A