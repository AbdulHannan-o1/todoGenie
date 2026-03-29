# Feature Specification: MCP Agent Integration

**Feature Branch**: `mcp-agent-integration`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Fix Agent to call MCP server via HTTP instead of direct function calls

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Calls MCP Server Tools (Priority: P1)

Agent must call MCP server tools via HTTP instead of executing functions directly in the same process.

**Why this priority**: This is the core requirement to meet Phase V hackathon specs. Currently Agent calls `@function_tool` decorated methods directly, but hackathon requires Agent → MCP Server (HTTP) → Tools.

**Independent Test**: Can be fully tested by verifying that Agent invokes tools by making HTTP requests to the MCP server, not by executing Python functions directly.

**Acceptance Scenarios**:

1. **Given** Agent has tools configured, **When** Agent decides to call `add_task`, **Then** Agent makes HTTP POST request to MCP server `/tools/add_task` endpoint
2. **Given** MCP server is running, **When** Agent calls a tool, **Then** Tool executes in MCP server process, not Agent process
3. **Given** Multiple tools are available, **When** Agent needs to use a tool, **Then** Agent discovers tools via MCP server `/tools` endpoint

---

### User Story 2 - Tool Discovery via MCP Server (Priority: P2)

Agent must discover available tools by querying the MCP server, not from hardcoded tool lists.

**Why this priority**: Ensures dynamic tool discovery and follows the MCP protocol correctly.

**Independent Test**: Can be tested by starting MCP server, querying `/tools` endpoint, and verifying Agent receives correct tool definitions.

**Acceptance Scenarios**:

1. **Given** MCP server is running, **When** Agent requests tool list, **Then** Agent receives JSON with all available tool schemas
2. **Given** New tool is added to MCP server, **When** Agent queries tools, **Then** Agent receives updated tool list

---

### User Story 3 - Tool Execution via MCP Client (Priority: P2)

Agent must use MCP Client to execute tools via HTTP instead of direct function calls.

**Why this priority**: Separates Agent logic from tool execution logic, enabling distributed deployment.

**Independent Test**: Can be tested by mocking MCP server and verifying Agent calls the MCP client's HTTP methods.

**Acceptance Scenarios**:

1. **Given** Agent needs to execute a tool, **When** Agent calls MCP client, **Then** MCP client makes HTTP request to MCP server
2. **Given** MCP server returns error, **When** Agent calls tool, **Then** Agent receives error response from MCP client

---

### User Story 4 - Agent Uses MCP Client (Priority: P1)

Agent must use MCP Client class to interact with MCP server, not direct HTTP calls.

**Why this priority**: Provides abstraction layer and consistent error handling.

**Independent Test**: Can be tested by verifying Agent imports and uses MCPClient class.

**Acceptance Scenarios**:

1. **Given** Agent needs to execute tools, **When** Agent code is inspected, **Then** Agent uses `mcp_client.call_tool()` method
2. **Given** MCP Client is initialized, **When** Agent runs, **Then** MCP Client makes HTTP requests to configured base_url

---

### Edge Cases

- What happens when MCP server is unreachable? Agent should fail gracefully with clear error message
- What happens when tool arguments are invalid? MCP server should return error, Agent should handle it
- What happens when Agent needs multiple tools in one turn? Agent should call MCP client multiple times
- What happens when MCP server returns malformed response? Agent should handle and log the error

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use OpenAI Agents SDK with Agent + Runner pattern
- **FR-002**: System MUST implement MCP Server using Official MCP SDK (not custom HTTP)
- **FR-003**: System MUST expose all 9 task tools via MCP Server (`add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`, `get_task_by_id`, `get_child_tasks`, `create_child_task`, `get_upcoming_reminders`)
- **FR-004**: System MUST allow Agent to discover tools by querying MCP server `/tools` endpoint
- **FR-005**: System MUST allow Agent to execute tools by calling MCP server `/tools/{tool_name}` endpoint via HTTP
- **FR-006**: System MUST use MCP Client class for all tool executions
- **FR-007**: System MUST support async tool execution
- **FR-008**: System MUST handle tool execution errors gracefully

### Key Entities

- **MCP Server**: HTTP server exposing tools via `/tools` and `/tools/{tool_name}` endpoints
- **MCP Client**: HTTP client that Agent uses to call MCP server tools
- **Agent**: OpenAI Agents SDK Agent that uses MCP Client for tool execution
- **Tool Functions**: Python functions that execute actual task operations (called by MCP server)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agent successfully calls MCP server tools via HTTP POST requests
- **SC-002**: Tool execution happens in MCP server process, not Agent process
- **SC-003**: All 9 tools are discoverable via MCP server `/tools` endpoint
- **SC-004**: Tool arguments are correctly passed to MCP server via JSON body
- **SC-005**: Tool errors are properly handled and reported back to Agent

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT PROCESS                                           │
│                                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────────┐   │
│  │   Agent     │───▶│   MCP       │───▶│  OpenAI Agents SDK                 │   │
│  │  (Runner)   │    │   Client    │    │  (Agent + Runner pattern)          │   │
│  └─────────────┘    └─────────────┘    └─────────────────────────────────────┘   │
│        │                        │                                                 │
│        │                        │ HTTP POST                                       │
│        │                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MCP SERVER PROCESS (Official MCP SDK)                     │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌────────────────────────────────┐  │  │
│  │  │   Server    │───▶│ Tool Router │───▶│  Tool Functions                │  │  │
│  │  │  (FastAPI)  │    │             │    │  - add_task()                  │  │  │
│  │  └─────────────┘    │  (Routes)   │    │  - list_tasks()                 │  │  │
│  │                     └─────────────┘    │  - update_task()                │  │  │
│  │                                      │  - complete_task()                │  │  │
│  │                                      │  - delete_task()                   │  │  │
│  │                                      │  - ... (9 total tools)            │  │  │
│  │                                      └────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                           DATABASE (PostgreSQL)                               │  │
│  │  - tasks, conversations, messages, users                                      │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| AI Framework | OpenAI Agents SDK (`agents` package) |
| MCP Server | Official MCP SDK (`mcp` package) |
| MCP Server Framework | FastAPI |
| MCP Client | Custom HTTP client using `httpx.AsyncClient` |
| Tool Functions | Python async functions |
| Tool Execution | MCP Server process (separate from Agent) |

## Implementation Notes

### Current Issues

1. Agent tools are decorated with `@function_tool` - Agent calls these directly
2. MCP Server uses custom HTTP (not Official MCP SDK)
3. No separation between Agent process and Tool execution

### Required Changes

1. Remove `@function_tool` decorators from Agent methods
2. Create MCP Server using Official MCP SDK's `Server` class
3. Implement MCP Server tools that call task operations
4. Create MCP Client that Agent uses to call MCP Server
5. Agent imports and uses MCP Client for tool execution
6. Tool execution happens in MCP Server process

### Official MCP SDK Reference

The Official MCP SDK provides:
- `mcp.server.Server` - MCP server implementation
- `mcp.server.stdio.stdio_server()` - stdio-based server
- `mcp.types.Tool` - Tool type definition
- Tool handlers and execution patterns

However, for HTTP-based MCP (more suitable for microservices):
- Use FastAPI as MCP server framework
- Expose tools via HTTP endpoints
- Agent calls tools via HTTP POST requests
