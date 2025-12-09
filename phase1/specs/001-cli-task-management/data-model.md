# Data Model: CLI Task Management

**Version**: 1.0
**Status**: Completed
**Author**: Gemini
**Last Updated**: 2025-12-06

## 1. Task Entity

- **Entity Name**: `Task`
- **Description**: Represents a single to-do item.

### Fields:

| Field       | Type   | Description                  | Validation Rules |
|-------------|--------|------------------------------|------------------|
| `id`        | `int`  | Unique identifier for the task | Required, unique |
| `description` | `str`  | The content of the task      | Required, not empty |
| `status`    | `str`  | The current status of the task | Must be "pending" or "completed" |

### State Transitions:

- A task is created with the "pending" status.
- A task can transition from "pending" to "completed".
- A task cannot transition from "completed" to "pending".
