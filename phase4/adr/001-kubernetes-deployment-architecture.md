# ADR 001: Kubernetes Deployment Architecture for TodoGenie Application

## Status
Accepted

## Date
2026-01-21

## Context
The TodoGenie application needs to be deployed to a local Kubernetes cluster for development and testing purposes. This requires containerizing both frontend and backend components, setting up proper networking between services, and creating a reliable deployment process using Helm charts.

## Decision
We decided to implement the following architecture:

**Containerization Strategy:**
- Frontend: Next.js application containerized with optimized multi-stage Docker build
- Backend: FastAPI application containerized with production-ready configuration
- Database: PostgreSQL deployed as StatefulSet with persistent volume claims

**Service Communication:**
- Internal service discovery using Kubernetes DNS names
- Next.js rewrites configured to proxy API requests to backend service
- Proper environment variable configuration for different deployment contexts

**Deployment Approach:**
- Helm charts for packaging and managing the entire application stack
- Minikube for local Kubernetes development environment
- Service-to-service communication via ClusterIP services
- Proper health checks and resource limits

**Specific Technical Choices:**
- Backend service name: `todogenie-release-backend` (from Helm chart)
- Frontend service name: `todogenie-release-frontend` (from Helm chart)
- Database: PostgreSQL with persistent storage
- Environment configuration: NEXT_PUBLIC_BACKEND_API_URL="" (empty for relative paths in browser)
- Next.js rewrites: Map `/api/*` paths to backend service

## Consequences

**Positive:**
- Consistent deployment across different environments
- Proper service isolation and scaling capabilities
- Standardized configuration management through Helm
- Reliable service-to-service communication
- Maintains all existing functionality while adding containerization

**Negative:**
- Increased complexity compared to direct deployment
- Additional operational overhead for Kubernetes cluster management
- Learning curve for team members unfamiliar with Kubernetes
- Potential networking issues when transitioning between local and cluster environments

## Alternatives Considered

**Alternative 1: Direct Docker Compose Deployment**
- Simpler setup with docker-compose
- Familiar to most developers
- Rejected because it doesn't provide the Kubernetes experience needed for production parity

**Alternative 2: Separate Helm Charts for Each Component**
- More granular control over individual components
- Independent deployment of frontend/backend/database
- Rejected because it adds complexity without significant benefit for this application size

**Alternative 3: Using Ingress Controller for External Access**
- Cleaner separation of concerns
- Better for production environments
- Rejected for local development due to ISP/network interference issues with custom hostnames

## References
- `/specs/002-k8s-deployment/spec.md` - Feature specification
- `/specs/002-k8s-deployment/plan.md` - Implementation plan
- `/helm-charts/todogenie/` - Helm chart implementation
- `/frontend/next.config.ts` - Next.js rewrite configuration
- `/frontend/Dockerfile` - Frontend containerization
- `/backend/Dockerfile` - Backend containerization