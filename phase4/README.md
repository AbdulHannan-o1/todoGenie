# Phase 4: Kubernetes Deployment

This phase focuses on deploying the TodoGenie application to a local Kubernetes cluster using Minikube and Helm charts.

## Overview

The TodoGenie application (consisting of a Next.js frontend and FastAPI backend) is packaged into Docker images and deployed to a Kubernetes cluster using Helm charts. The deployment includes:

- Frontend service (Next.js application) on port 3000
- Backend service (FastAPI application) on port 8000
- PostgreSQL database with persistent storage
- Network policies for security
- ConfigMaps and Secrets for configuration
- Service accounts with minimal permissions

## Prerequisites

- Docker Desktop (with Kubernetes enabled) or Minikube
- Helm 3
- kubectl
- Git

## Deployment Steps

1. **Start Minikube** (if using Minikube):
   ```bash
   minikube start --memory=4096 --cpus=2
   ```

2. **Build Docker Images**:
   ```bash
   cd backend
   docker build -t todogenie-backend:latest .
   cd ../frontend
   docker build -t todogenie-frontend:latest .
   cd ..
   ```

3. **Load Images into Minikube** (if using Minikube):
   ```bash
   minikube image load todogenie-backend:latest
   minikube image load todogenie-frontend:latest
   ```

4. **Deploy Using Helm**:
   ```bash
   cd helm-charts
   helm install todogenie ./todogenie --namespace todogenie --create-namespace
   ```

## Automated Deployment

Alternatively, you can use the automated deployment script:

```bash
./deploy.sh
```

## Accessing the Application

After deployment, you can access the services in the following ways:

- **Via kubectl port-forward**:
  ```bash
  kubectl port-forward -n todogenie svc/todogenie-frontend 3000:3000
  kubectl port-forward -n todogenie svc/todogenie-backend 8000:8000
  ```

- **Via Minikube service**:
  ```bash
  minikube service todogenie-frontend -n todogenie
  ```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (MINIKUBE)                │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   FRONTEND      │  │    BACKEND      │  │   DATABASE      │ │
│  │   (Next.js)     │  │   (FastAPI)     │  │ (PostgreSQL)    │ │
│  │   Port: 3000    │  │   Port: 8000    │  │   Port: 5432    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│              │                 │                    │          │
│              └─────────────────┼────────────────────┘          │
│                                │                               │
│                    ┌─────────────────────────┐                 │
│                    │     MCP SERVER          │                 │
│                    │   (Part of Backend)     │                 │
│                    └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

The deployment follows these architectural principles:

- **Separation of Concerns**: Frontend and backend are deployed as separate services
- **Persistent Storage**: PostgreSQL database with persistent volume claims
- **Configuration Management**: Using Kubernetes ConfigMaps and Secrets
- **Security**: Network policies and minimal RBAC permissions
- **Observability**: Ready for integration with monitoring solutions
- **Service Communication**: Next.js rewrites proxy frontend API calls to backend service

## Helm Chart Structure

The Helm chart includes:

- `Chart.yaml`: Chart definition and dependencies
- `values.yaml`: Default configuration values
- `templates/`: Kubernetes resource templates
  - Deployments for frontend and backend
  - Services for internal communication
  - ConfigMaps for configuration
  - Secrets for sensitive data
  - Network policies for security
  - Service accounts with minimal permissions
  - Ingress for external access (optional)

## Cleanup

To remove the deployment:

```bash
helm uninstall todogenie -n todogenie
kubectl delete namespace todogenie
```

## Troubleshooting

- If images are not found, ensure they are loaded into your Kubernetes cluster (Minikube or kind)
- Check pod status: `kubectl get pods -n todogenie`
- View logs: `kubectl logs -l app=backend -n todogenie`
- Verify service connectivity: `kubectl get svc -n todogenie` 