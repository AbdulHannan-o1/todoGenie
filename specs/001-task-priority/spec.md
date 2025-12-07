# Feature Specification: Task Priority System

**Feature Branch**: `001-task-priority`  
**Created**: 2025-12-07  
**Status**: Draft  
**Input**: User description: "1. Priority System Add priority levels: Low Medium High Stored in memory. the priority session should be implemtned in a way that when user is creating a task is and add title and description the next question it should as should be to set te pririty level high,low if it its's empty then there is no priority for thhe task note (make the current logic remain same )"

## User Scenarios & Testing

### User Story 1 - Add Task with Priority (Priority: P1)

As a user, I want to be able to assign a priority level (Low, Medium, High) to a task when I create it, so that I can easily identify and manage the importance of my tasks. If I choose not to assign a priority, the task should still be created.

**Why this priority**: This is the core functionality of the feature, directly addressing the user's need to prioritize tasks. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by creating tasks with and without priority assignments and verifying the stored priority.

**Acceptance Scenarios**:

1.  **Given** the user is creating a new task, **When** they enter a title and description, **Then** they are prompted to set a priority level (Low, Medium, High).
2.  **Given** the user is prompted for priority, **When** they select "High", **Then** the task is created with "High" priority.
3.  **Given** the user is prompted for priority, **When** they select "Medium", **Then** the task is created with "Medium" priority.
4.  **Given** the user is prompted for priority, **When** they select "Low", **Then** the task is created with "Low" priority.
5.  **Given** the user is prompted for priority, **When** they do not select a priority, **Then** the task is created with no priority.

### Edge Cases

-   What happens if the user provides an invalid input for priority? (System should handle gracefully, e.g., default to no priority or re-prompt).
-   How is priority displayed when a task has no priority? (Should be clearly indicated as "None" or similar).

## Requirements

### Functional Requirements

-   **FR-001**: The system MUST allow tasks to have an associated priority level.
-   **FR-002**: The system MUST support "Low", "Medium", and "High" as valid priority levels.
-   **FR-003**: The system MUST allow tasks to be created without a priority level.
-   **FR-004**: When creating a task, after providing a title and description, the user MUST be prompted to set a priority level.
-   **FR-005**: The system MUST store priority levels in memory.

### Key Entities

-   **Task**: Represents a single task with attributes like title, description, and priority.
    -   Attributes: `title` (string), `description` (string), `priority` (enum: Low, Medium, High, or null).

## Success Criteria

### Measurable Outcomes

-   **SC-001**: 100% of tasks created with a specified priority are correctly stored with that priority.
-   **SC-002**: 100% of tasks created without a specified priority are correctly stored as having no priority.
-   **SC-003**: Users can successfully assign a priority level to a task during creation without encountering errors.