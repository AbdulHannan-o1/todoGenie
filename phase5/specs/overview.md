# Phase V: Advanced Cloud Deployment - Todo AI Chatbot

## Project Overview

Phase V represents the culmination of the Todo app evolution, transforming it into a **cloud-native, event-driven, AI-powered distributed system** deployed on DigitalOcean Kubernetes (DOKS) with Kafka for event streaming and Dapr for distributed application runtime.

## Current Phase Status

**Phase V: Advanced Cloud Deployment**

This phase builds upon:
- Phase I: Console app (Python)
- Phase II: Full-stack web app (Next.js + FastAPI + Neon DB)
- Phase III: AI Chatbot (OpenAI Agents SDK + MCP Server)
- Phase IV: Local Kubernetes (Minikube + Helm)

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | OpenAI ChatKit (Hosted) |
| **AI Framework** | OpenAI Agents SDK (Agent + Runner) |
| **MCP Server** | Official MCP SDK (Python) |
| **Backend API** | FastAPI |
| **ORM** | SQLModel |
| **Database** | Neon Serverless PostgreSQL |
| **Event Streaming** | Kafka (Redpanda Cloud) |
| **Distributed Runtime** | Dapr (Pub/Sub, State, Bindings, Secrets) |
| **Orchestration** | DigitalOcean Kubernetes (DOKS) |
| **Package Manager** | Helm Charts |
| **CI/CD** | GitHub Actions |
| **Authentication** | Better Auth with JWT |

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              DIGITALOCEAN KUBERNETES CLUSTER                         │
│                                                                                       │
│  ┌─────────────────┐                                                                  │
│  │   OpenAI        │                                                                  │
│  │   ChatKit       │                                                                  │
│  │   (Hosted)      │                                                                  │
│  └────────┬────────┘                                                                  │
│           │                                                                            │
│           ▼                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI Pod (with Dapr Sidecar)                         │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────────┐ │  │
│  │  │  Chat API   │    │   OpenAI    │    │           MCP Server                │ │  │
│  │  │  Endpoint   │───▶│   Agents    │───▶│         (Official MCP SDK)          │ │  │
│  │  │  /api/chat  │    │   SDK        │    │                                     │ │  │
│  │  └─────────────┘    └─────────────┘    └─────────────┬───────────────────────┘ │  │
│  │                                                      │                          │  │
│  │                    ┌─────────────────────────────────┘                          │  │
│  │                    │                                                             │  │
│  │                    ▼                                                             │  │
│  │         ┌──────────────────────┐                                                │  │
│  │         │   DAPR SIDECAR       │                                                │  │
│  │         │  - Pub/Sub (Kafka)   │                                                │  │
│  │         │  - State (Postgres)  │                                                │  │
│  │         │  - Bindings (Cron)   │                                                │  │
│  │         │  - Secrets (K8s)     │                                                │  │
│  │         └──────────┬───────────┘                                                │  │
│  └─────────────────────┼───────────────────────────────────────────────────────────┘  │
│                        │                                                               │
│                        │                                                               │
│  ┌─────────────────────┼───────────────────────────────────────────────────────────┐  │
│  │                     │                    KAFKA CLUSTER (Redpanda Cloud)          │  │
│  │                     │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │                     ├──▶│ task-events │  │ reminders   │  │ task-updates│       │  │
│  │                     │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │  │
│  │                     │          │                │                │               │  │
│  │                     │   ┌──────┴────────────────┴────────────────┴───────┐       │  │
│  │                     │   │              Kafka Consumers                    │       │  │
│  │                     │   │  ┌──────────────┐  ┌──────────────┐            │       │  │
│  │                     │   │  │ Notification │  │  Recurring   │            │       │  │
│  │                     │   │  │   Service    │  │   Service    │            │       │  │
│  │                     │   │  └──────────────┘  └──────────────┘            │       │  │
│  │                     │   └─────────────────────────────────────────────────┘       │  │
│  └─────────────────────┼─────────────────────────────────────────────────────────────┘  │
│                        │                                                                 │
│                        ▼                                                                 │
│              ┌──────────────────┐                                                        │
│              │  Neon DB         │                                                        │
│              │  (PostgreSQL)    │                                                        │
│              │  - tasks         │                                                        │
│              │  - conversations │                                                        │
│              │  - messages      │                                                        │
│              │  - users         │                                                        │
│              └──────────────────┘                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Feature Requirements

### Basic Level (Required)
- [x] Add Task
- [x] Delete Task
- [x] Update Task
- [x] View Task List
- [x] Mark as Complete

### Intermediate Level (Required for Phase V)
- [ ] Priorities & Tags/Categories
- [ ] Search & Filter
- [ ] Sort Tasks

### Advanced Level (Required for Phase V)
- [ ] Recurring Tasks
- [ ] Due Dates & Time Reminders

### Event-Driven Features (Phase V)
- [ ] Kafka-based reminder notifications
- [ ] Recurring task auto-creation
- [ ] Real-time task sync across clients
- [ ] Activity/audit log

### Dapr Integration (Phase V)
- [ ] Pub/Sub for Kafka abstraction
- [ ] State management for conversations
- [ ] Cron bindings for scheduled reminders
- [ ] Secrets management for credentials

## Deliverables

1. **GitHub Repository** with:
   - `/phase5/specs` - All specification files
   - `/phase5/frontend` - ChatKit-based UI
   - `/phase5/backend` - FastAPI + OpenAI Agents SDK + MCP Server
   - `/phase5/helm` - Helm charts for DOKS
   - `/phase5/.github/workflows` - CI/CD pipeline

2. **Deployed Applications**:
   - Frontend: Vercel/Netlify with ChatKit
   - Backend: DigitalOcean Kubernetes (DOKS)
   - Kafka: Redpanda Cloud (Serverless)

3. **Demo Video** (max 90 seconds)

## Success Criteria

| Criterion | Requirement |
|-----------|-------------|
| **OpenAI Agents SDK** | Must use Agent + Runner pattern |
| **MCP Server** | Must use Official MCP SDK |
| **Kafka Integration** | Must publish/subscribe to events |
| **Dapr Integration** | Must use Pub/Sub, State, Bindings |
| **Kubernetes Deployment** | Must run on DOKS with Helm |
| **CI/CD Pipeline** | Must have GitHub Actions |
| **Stateless Chat** | Server holds no conversation state |

## References

- [Hackathon Project Details](../../hackathon-project-details.md)
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Dapr Documentation](https://docs.dapr.io/)
- [Redpanda Cloud Documentation](https://docs.redpanda.com/)
