# Phase 4: Kubernetes Deployment - Implementation Notes

## Overview
This document provides implementation notes for the Kubernetes deployment of the TodoGenie application, including Docker containerization, Helm chart deployment, and configuration details.

## Containerization Process

### Frontend Containerization (Next.js)
- **Base Image**: node:20-alpine
- **Build Process**: Multi-stage build with dependencies and production stages
- **Output Mode**: Standalone (output: 'standalone' in next.config.ts)
- **Security**: Non-root user (nextjs:nodejs with UID/GID 1001)
- **Port**: 3000

### Backend Containerization (FastAPI)
- **Base Image**: python:3.11-slim
- **Build Process**: Multi-stage build with dependencies and runtime stages
- **Security**: Non-root user configuration
- **Port**: 8000

## Docker Build Requirements

### Frontend (Next.js)
1. **next.config.ts** must include `output: 'standalone'`
2. **.dockerignore** must exclude test files (cypress/, etc.)
3. **TypeScript** syntax must be correct in all page components
4. **Params handling** in dynamic routes must use proper destructuring

### Backend (FastAPI)
1. **requirements.txt** must be properly formatted
2. **Dockerfile** should follow multi-stage build pattern
3. **Security contexts** should run as non-root users

## Kubernetes Deployment Architecture

### Helm Chart Structure
```
helm-charts/
└── todogenie/
    ├── Chart.yaml          # Chart metadata and dependencies
    ├── values.yaml         # Default configuration values
    ├── templates/          # Kubernetes resource templates
    │   ├── backend-deployment.yaml
    │   ├── backend-service.yaml
    │   ├── frontend-deployment.yaml
    │   ├── frontend-service.yaml
    │   ├── postgres-deployment.yaml (subchart)
    │   ├── postgres-service.yaml (subchart)
    │   ├── networkpolicy.yaml
    │   ├── configmap.yaml
    │   ├── secrets.yaml
    │   ├── serviceaccount.yaml
    │   └── _helpers.tpl
    └── README.md           # Chart documentation
```

### Service Architecture
- **Frontend Service**: Next.js application on port 3000
- **Backend Service**: FastAPI application on port 8000
- **Database Service**: PostgreSQL on port 5432
- **Internal Communication**: Services communicate via Kubernetes DNS

### Security Configuration
- **Network Policies**: Restrict communication between services
- **RBAC**: Minimal required permissions for service accounts
- **Security Contexts**: Non-root containers with minimal capabilities
- **Secrets Management**: Kubernetes secrets for sensitive data

## Deployment Process

### Prerequisites
1. **Docker Images**: Built and available (locally or in registry)
2. **Kubernetes Cluster**: Minikube or cloud cluster ready
3. **Helm**: Helm 3 installed and configured
4. **kubectl**: kubectl configured for cluster access

### Steps
1. **Build Images**:
   ```bash
   # Frontend
   cd frontend
   docker build -t todogenie-frontend:latest .

   # Backend
   cd ../backend
   docker build -t todogenie-backend:latest .
   ```

2. **Load Images to Minikube** (if using Minikube):
   ```bash
   minikube image load todogenie-frontend:latest
   minikube image load todogenie-backend:latest
   ```

3. **Deploy with Helm**:
   ```bash
   cd ../helm-charts
   helm install todogenie ./todogenie --namespace todogenie --create-namespace
   ```

4. **Verify Deployment**:
   ```bash
   kubectl get pods -n todogenie
   kubectl get svc -n todogenie
   kubectl get deployments -n todogenie
   ```

## Configuration Parameters

### Frontend Configuration
- `frontend.replicaCount`: Number of frontend pods (default: 1)
- `frontend.image.repository`: Frontend image name (default: todogenie-frontend)
- `frontend.image.tag`: Image tag (default: latest)
- `frontend.service.type`: Service type (default: ClusterIP)
- `frontend.service.port`: Port number (default: 3000)

### Backend Configuration
- `backend.replicaCount`: Number of backend pods (default: 1)
- `backend.image.repository`: Backend image name (default: todogenie-backend)
- `backend.image.tag`: Image tag (default: latest)
- `backend.service.type`: Service type (default: ClusterIP)
- `backend.service.port`: Port number (default: 8000)

### Database Configuration
- `postgresql.enabled`: Enable PostgreSQL subchart (default: true)
- `postgresql.auth.postgresPassword`: Database password
- `postgresql.auth.database`: Database name
- `postgresql.primary.persistence.size`: Storage size (default: 8Gi)

## Monitoring and Health Checks

### Health Probes
- **Backend**: `/health` endpoint for liveness/readiness
- **Frontend**: Root path `/` for liveness/readiness
- **Database**: Built-in PostgreSQL health checks

### Resource Requirements
- **Frontend**: 128Mi-512Mi memory, 100m-500m CPU
- **Backend**: 128Mi-512Mi memory, 100m-500m CPU
- **Database**: 128Mi-512Mi memory, 100m-500m CPU

## Troubleshooting

### Common Issues
1. **Image Pull Errors**: Verify images are built and loaded to cluster
2. **Service Connectivity**: Check network policies and service configurations
3. **Database Connection**: Verify database is running and credentials are correct
4. **Health Check Failures**: Check application logs for startup issues

### Verification Commands
```bash
# Check pod status
kubectl get pods -n todogenie

# Check service connectivity
kubectl get svc -n todogenie

# Check logs
kubectl logs -l app=backend -n todogenie
kubectl logs -l app=frontend -n todogenie

# Port forward for testing
kubectl port-forward -n todogenie svc/todogenie-frontend 3000:3000
kubectl port-forward -n todogenie svc/todogenie-backend 8000:8000
```

## Scaling Considerations

### Horizontal Scaling
- **Frontend**: Can scale based on traffic
- **Backend**: Can scale based on API load
- **Database**: Scale vertically (storage) or use read replicas

### Resource Optimization
- **Memory**: Adjust based on application usage patterns
- **CPU**: Configure based on processing requirements
- **Storage**: Configure based on data growth projections

## Security Best Practices

### Network Security
- Use Network Policies to restrict traffic
- Implement service mesh for advanced traffic control
- Use TLS for service-to-service communication

### Access Control
- Implement RBAC with minimal required permissions
- Use service accounts with specific roles
- Regularly rotate secrets and credentials

### Image Security
- Use minimal base images
- Scan images for vulnerabilities
- Run containers as non-root users
- Implement runtime security monitoring