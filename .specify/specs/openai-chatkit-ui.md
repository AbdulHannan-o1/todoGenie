# Feature Specification: OpenAI ChatKit UI Integration

**Feature Branch**: `openai-chatkit-ui`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Replace custom Next.js frontend with OpenAI ChatKit (Hosted)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ChatKit UI Integration (Priority: P1)

Replace custom Next.js frontend with OpenAI ChatKit hosted UI for task management.

**Why this priority**: This is the core requirement to meet Phase V hackathon specs. The hackathon requires OpenAI ChatKit as the frontend technology.

**Independent Test**: Can be fully tested by verifying that users can chat with the AI agent through ChatKit UI and task operations work correctly.

**Acceptance Scenarios**:

1. **Given** User opens application, **When** ChatKit UI loads, **Then** ChatKit interface is displayed
2. **Given** User sends message, **When** Message is received, **Then** AI agent responds via ChatKit
3. **Given** User creates a task via chat, **When** Task is created, **Then** Task appears in task list
4. **Given** ChatKit is connected, **When** User types message, **Then** Message is sent to backend API

---

### User Story 2 - ChatKit Authentication (Priority: P2)

ChatKit must authenticate users and maintain session state.

**Why this priority**: Proper authentication is required for secure access to the application.

**Independent Test**: Can be tested by verifying login/logout flow and session persistence.

**Acceptance Scenarios**:

1. **Given** User visits application, **When** ChatKit initializes, **Then** User is prompted to login
2. **Given** User logs in, **When** Session is established, **Then** ChatKit remains connected
3. **Given** User logs out, **When** Session is terminated, **Then** ChatKit disconnects

---

### User Story 3 - Task Operations via Chat (Priority: P1)

Users must be able to create, view, update, and delete tasks through chat interface.

**Why this priority**: Core functionality - users need to manage tasks via AI assistant.

**Independent Test**: Can be tested by sending chat commands to create/list/update/delete tasks.

**Acceptance Scenarios**:

1. **Given** User sends "add a task called buy groceries", **When** Agent processes, **Then** Task is created
2. **Given** User sends "show me my tasks", **When** Agent processes, **Then** Tasks are listed
3. **Given** User sends "mark task 1 as complete", **When** Agent processes, **Then** Task is completed
4. **Given** User sends "delete task 2", **When** Agent processes, **Then** Task is deleted

---

### Edge Cases

- What happens when ChatKit connection is lost? UI should show reconnection status
- What happens when user is not authenticated? ChatKit should show login prompt
- What happens when agent takes long to respond? UI should show loading indicator
- What happens when backend API returns error? ChatKit should display error message

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use OpenAI ChatKit (Hosted) as the frontend UI
- **FR-002**: System MUST integrate ChatKit with backend chat API endpoint
- **FR-003**: System MUST handle authentication via ChatKit
- **FR-004**: System MUST display messages in ChatKit interface
- **FR-005**: System MUST allow users to send text messages via ChatKit
- **FR-006**: System MUST display AI responses in ChatKit interface
- **FR-007**: System MUST support task operations through chat commands

### Key Entities

- **ChatKit**: OpenAI's hosted chat UI component
- **ChatKit Instance**: Client-side ChatKit connection to OpenAI servers
- **Chat Message**: User message and AI response displayed in ChatKit
- **User Session**: Authentication state managed by ChatKit

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access ChatKit UI without custom frontend code
- **SC-002**: Users can send messages and receive AI responses in real-time
- **SC-003**: Task operations work seamlessly through ChatKit interface
- **SC-004**: Authentication flow works correctly with ChatKit

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              CHATKIT UI (HOSTED)                                     │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                       OpenAI ChatKit JavaScript SDK                         │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌────────────────────────────────┐   │   │
│  │  │   ChatKit   │───▶│   Channel   │───▶│   User Interface               │   │   │
│  │  │   Widget    │    │   (Room)    │    │   - Message Input              │   │   │
│  │  └─────────────┘    └─────────────┘    │   - Message List               │   │   │
│  │                                        │   - Task Actions                │   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                        │                    │                                       │
│                        │ OpenAI API         │ OpenAI API                            │
│                        │                    │                                       │
│                        ▼                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    YOUR BACKEND API                                         │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌────────────────────────────────┐   │   │
│  │  │  Chat API   │───▶│   Agent     │───▶│   MCP Server (HTTP)            │   │   │
│  │  │  /api/chat  │    │  (Runner)   │    │   - add_task                   │   │   │
│  │  └─────────────┘    │             │    │   - list_tasks                 │   │   │
│  │                     └─────────────┘    │   - update_task                │   │   │
│  │                                      │   - complete_task                │   │   │
│  │                                      │   - delete_task                   │   │   │
│  │                                      └────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend UI | OpenAI ChatKit (Hosted) |
| Chat SDK | OpenAI ChatKit JavaScript SDK |
| Authentication | OpenAI ChatKit Auth |
| Backend API | FastAPI (existing) |
| AI Agent | OpenAI Agents SDK (existing) |
| MCP Server | HTTP-based (existing) |

## Implementation Notes

### OpenAI ChatKit Overview

OpenAI ChatKit is a hosted, fully managed chat UI that includes:
- Real-time chat interface
- Message history
- User authentication
- Customizable styling
- Mobile-responsive design
- No frontend code required

### ChatKit Setup Steps

1. **Get OpenAI API Key** for ChatKit
2. **Create ChatKit instance** with OpenAI API key
3. **Connect to ChatKit** and initialize the widget
4. **Handle authentication** using OpenAI's auth flow
5. **Customize appearance** with CSS/branding

### Integration Approach

Since ChatKit is a hosted UI, integration is minimal:
- No React/Next.js frontend code needed
- Use ChatKit JavaScript SDK in HTML/JS
- Connect to backend chat API endpoint
- Handle authentication via OpenAI's auth flow

### Existing Custom Frontend

The current `phase5/frontend/` is a custom Next.js app that will be replaced by ChatKit.
