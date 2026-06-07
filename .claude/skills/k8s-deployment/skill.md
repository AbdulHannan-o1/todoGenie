# Kubernetes Deployment Skill

## Overview
This skill provides comprehensive guidance for deploying full-stack applications to Kubernetes clusters using Helm charts. It covers the complete deployment workflow including containerization, Helm chart creation, security implementation, and cloud database integration.

## Implementation Approach

### Complete Kubernetes Deployment Workflow
The deployment process includes:
- Containerization of frontend and backend applications
- Helm chart creation with all necessary templates
- Security implementation with Network Policies and RBAC
- Cloud database integration (NeonDB, PostgreSQL)
- Deployment automation and monitoring setup

### Key Components
1. **Docker Containerization**: Multi-stage builds for optimized images
2. **Helm Chart Creation**: Complete chart with deployments, services, configs
3. **Security Implementation**: Network policies, RBAC, security contexts
4. **Database Integration**: Cloud database connection and configuration
5. **Automation**: Deployment scripts and CI/CD setup

## Kubernetes Deployment Implementation

### Containerization Process
- Create optimized Dockerfiles for Next.js frontend
- Create optimized Dockerfiles for FastAPI backend
- Implement multi-stage builds to reduce image size
- Configure proper environment variable handling
- Set up security contexts (non-root containers)

### Helm Chart Structure
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

### Security Implementation
- Network Policies to restrict communication between services
- Minimal RBAC permissions with service accounts
- Proper security contexts (non-root containers)
- Secret management for sensitive data

## Key Implementation Details

### Prerequisites
- Kubernetes cluster access (Minikube, EKS, GKE, AKS)
- Helm 3 installed
- Docker images built and available
- Cloud database (NeonDB) connection string

### Core Files Created
1. `helm-charts/todogenie/Chart.yaml` - Chart definition
2. `helm-charts/todogenie/values.yaml` - Default values
3. `helm-charts/todogenie/templates/*.yaml` - Kubernetes templates
4. `deploy.sh` - Automated deployment script
5. `Dockerfile` - Containerization files for each service

### Deployment Process
1. Build Docker images for frontend and backend
2. Load images into Kubernetes cluster (if using Minikube)
3. Install Helm chart with proper configurations
4. Verify deployment and service connectivity
5. Access application through port forwarding or ingress

## Environment Configuration

### Kubernetes Environment Variables
**Backend:**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

**Frontend:**
```
NEXT_PUBLIC_BACKEND_API_URL=http://backend-service:8000
```

### Helm Values Configuration
```
frontend:
  replicaCount: 1
  image:
    repository: todogenie-frontend
    tag: latest
  service:
    type: ClusterIP
    port: 3000

backend:
  replicaCount: 1
  image:
    repository: todogenie-backend
    tag: latest
  service:
    type: ClusterIP
    port: 8000

postgresql:
  enabled: true
  auth:
    postgresPassword: "postgres"
    database: "todogenie_db"
```

## Security Considerations
- Network Policies to restrict traffic between pods
- RBAC with minimal required permissions
- Non-root containers for security
- Proper secret management for sensitive data
- Resource limits to prevent abuse

## Troubleshooting Tips

### Common Deployment Issues
**Symptoms:** Pods failing to start, images not found
**Solutions:**
- Verify Docker images are built and available
- Check image pull secrets if using private registries
- Verify Kubernetes cluster access and permissions
- Check resource availability in cluster

**Symptoms:** Services not accessible, connection timeouts
**Solutions:**
- Check service configurations and ports
- Verify network policies aren't blocking traffic
- Check if pods are running and ready
- Verify database connection strings

### Debugging Steps
1. Check pod status: `kubectl get pods -n <namespace>`
2. View pod logs: `kubectl logs <pod-name> -n <namespace>`
3. Describe pod for details: `kubectl describe pod <pod-name> -n <namespace>`
4. Check services: `kubectl get svc -n <namespace>`
5. Verify Helm release: `helm status <release-name>`

## Future Improvements

### Scaling Considerations
- Implement Horizontal Pod Autoscaling
- Add resource monitoring and alerts
- Set up log aggregation and analysis
- Implement blue-green deployment strategies

### Advanced Features
- Service Mesh integration (Istio, Linkerd)
- Advanced monitoring with Prometheus/Grafana
- Automated security scanning
- GitOps deployment workflows

## Testing Checklist

### Deployment Verification
- [ ] All pods are running and ready
- [ ] Services are accessible within cluster
- [ ] External access works (if configured)
- [ ] Database connection is established
- [ ] Frontend can communicate with backend
- [ ] Security policies are applied correctly
- [ ] Resource limits are respected
- [ ] Health checks are passing