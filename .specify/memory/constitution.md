# TaskMind Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### I. Spec-First Design
<!-- Example: I. Library-First -->
All features must start with a formal specification; no implementation without a clear blueprint. Specs must include task structure, command syntax, system behavior, error handling, and acceptance criteria. This ensures maintainable, AI-driven, spec-compliant development.

### II. CLI-First Interface
<!-- Example: II. CLI Interface -->
The application is CLI-based. All commands follow a strict text-based protocol: stdin/arguments → stdout, errors → stderr, Optional: JSON + human-readable output for future integrations

### III. In-Memory Storage (NON-NEGOTIABLE)
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
No database or file persistence. All tasks exist in variables, dictionaries, or lists. Data resets on exit. This guarantees stateless, lightweight behavior compatible with npm/uv deployment.

### IV. CRUD and AI-Driven Enhancements
<!-- Example: IV. Integration Testing -->
Basic CRUD (Add, List, Update, Complete, Delete) is mandatory. Optional AI-driven features include: Auto-categorization, Deadline suggestions, Task title improvements

### V. Modular Architecture
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
All code must be modular: /spec.py → app specification, /app.py → CLI runner, /storage.py → in-memory task manager, /commands.py → command parser, /utils.py → helpers, This allows clear separation of concerns and future extensibility.

### VI. Observability & User Feedback
Console outputs must provide clear success/error messages. Use optional rich-colored feedback (green for success, red for errors). Commands must handle invalid inputs gracefully, with guidance or help prompts.

## Additional Constraints
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->
Python 3.10+ required, Optional libraries: rich (for colored console UI), openai or SpecKit Plus (for AI features), Must be deployable as npm/uv package for global CLI use: npm install -g todo-cli, No external storage or persistent databases, In-memory data must be fully reset on program exit

## Development Workflow
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->
Spec-Driven: Implementations must strictly follow the constitution/spec, Testing: Unit tests (pytest) for storage and utility functions. Integration tests for CLI commands, Code Review: All code reviewed for spec compliance, modularity, and maintainability, Documentation: Every module must include comments describing purpose, behavior, and edge cases, Error Handling: All commands must fail gracefully, showing informative messages.

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->
The constitution supersedes all other coding practices. Any amendment must be documented, approved, and a migration plan provided. All PRs and reviews must verify spec compliance, Complexity must be justified, Use /spec.py as the single source of truth for runtime behavior and future enhancements

**Version**: 1.1.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
