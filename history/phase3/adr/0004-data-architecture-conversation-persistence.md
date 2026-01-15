# ADR-0004: Data Architecture for Conversation Persistence

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-20
- **Feature:** 001-ai-chatbot-voice
- **Context:** Need to persist conversation state between user interactions to maintain context for the AI agent. The solution must ensure reliability, support concurrent conversations, maintain user data isolation, and integrate with the existing PostgreSQL database infrastructure.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Storage Location**: Neon Serverless PostgreSQL database
- **Entity Design**: New Conversation and Message entities with proper relationships
- **Persistence Strategy**: Database-based conversation state storage
- **Integration**: Extension of existing data model with new tables and indexes

## Consequences

### Positive

- Reliable persistence that survives system restarts
- Support for concurrent conversations per user
- Proper user data isolation through database constraints
- Consistency with existing data patterns and infrastructure
- Full backup and recovery capabilities through database features
- Efficient querying with appropriate indexes
- ACID compliance for data integrity

### Negative

- Additional database tables and storage requirements
- More complex queries when retrieving conversation history
- Potential performance impact as conversation history grows
- Additional migration requirements
- More complex data management as conversation data accumulates over time

## Alternatives Considered

- **In-memory storage**: Would lose state on restarts, unsuitable for persistent conversations
- **Session storage**: Limited for long-running conversations, not appropriate for chat history
- **External cache (Redis)**: Adds additional dependency, potential consistency issues with primary data store
- **File-based storage**: Would complicate deployment, backup, and scaling
- **Separate document database**: Would introduce additional technology and complexity without clear benefits

## References

- Feature Spec: phase3/specs/001-ai-chatbot-voice/spec.md
- Implementation Plan: phase3/specs/001-ai-chatbot-voice/plan.md
- Data Model: phase3/specs/001-ai-chatbot-voice/data-model.md
- Research: phase3/specs/001-ai-chatbot-voice/research.md
- Evaluator Evidence: phase3/specs/001-ai-chatbot-voice/research.md