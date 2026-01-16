# Deployment Automation Skill

## Overview
This skill provides comprehensive guidance for automating Kubernetes deployments with scripts, CI/CD pipelines, and infrastructure-as-code tools. It covers automated deployment workflows for different platforms (Minikube, EKS, GKE, AKS) with monitoring and logging integration.

## Implementation Approach

### Complete Deployment Automation Workflow
The automation process includes:
- Automated Docker image building and tagging
- Kubernetes cluster preparation
- Helm chart deployment with configuration
- Health check and validation
- Monitoring and alerting setup
- Rollback procedures
- Post-deployment verification

### Key Components
1. **Docker Automation**: Automated image building and management
2. **Kubernetes Preparation**: Cluster setup and configuration
3. **Helm Deployment**: Automated chart installation and updates
4. **Health Checks**: Service validation and monitoring
5. **Rollback Procedures**: Automated rollback capabilities
6. **CI/CD Integration**: Pipeline setup for automated deployments

## Deployment Automation Implementation

### Automated Deployment Script Structure
- Pre-flight checks and validations
- Docker image building and tagging
- Kubernetes cluster connection
- Helm chart deployment
- Service validation and health checks
- Post-deployment verification
- Error handling and rollback procedures

### Platform-Specific Automation
- **Minikube**: Local development cluster automation
- **EKS**: Amazon Elastic Kubernetes Service deployment
- **GKE**: Google Kubernetes Engine deployment
- **AKS**: Azure Kubernetes Service deployment
- **Generic K8s**: Standard Kubernetes cluster deployment

## Key Implementation Details

### Automated Deployment Script Template
```
#!/bin/bash

# Deployment script for Application
set -e  # Exit on any error

echo "Starting Application Kubernetes deployment..."

# Configuration variables
APP_NAME="application"
NAMESPACE="${APP_NAME}"
HELM_CHART="./helm-charts/${APP_NAME}"
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# Function to validate prerequisites
validate_prerequisites() {
    echo "Validating prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        echo "kubectl is required but not installed. Aborting."
        exit 1
    fi

    if ! command -v helm &> /dev/null; then
        echo "helm is required but not installed. Aborting."
        exit 1
    fi

    echo "Prerequisites validated successfully."
}

# Function to build Docker images
build_images() {
    echo "Building Docker images..."

    cd backend
    docker build -t "${APP_NAME}-backend:${IMAGE_TAG}" .
    cd ..

    cd frontend
    docker build -t "${APP_NAME}-frontend:${IMAGE_TAG}" .
    cd ..

    echo "Docker images built successfully."
}

# Function to prepare Kubernetes cluster
prepare_cluster() {
    echo "Preparing Kubernetes cluster..."

    # Create namespace if it doesn't exist
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

    echo "Kubernetes cluster prepared."
}

# Function to deploy using Helm
deploy_helm() {
    echo "Deploying using Helm..."

    # Install or upgrade Helm release
    helm upgrade --install "${APP_NAME}" "${HELM_CHART}" \
        --namespace "${NAMESPACE}" \
        --create-namespace \
        --set backend.image.tag="${IMAGE_TAG}" \
        --set frontend.image.tag="${IMAGE_TAG}" \
        --wait \
        --timeout=10m

    echo "Helm deployment completed."
}

# Function to validate deployment
validate_deployment() {
    echo "Validating deployment..."

    # Wait for deployments to be ready
    kubectl wait --for=condition=ready pod -l app=backend -n "${NAMESPACE}" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=frontend -n "${NAMESPACE}" --timeout=300s

    # Check service status
    kubectl get svc -n "${NAMESPACE}"

    echo "Deployment validated successfully."
}

# Main execution
main() {
    validate_prerequisites
    build_images
    prepare_cluster
    deploy_helm
    validate_deployment

    echo ""
    echo "Application deployed successfully!"
    echo "Namespace: ${NAMESPACE}"
    echo "Helm Release: ${APP_NAME}"
    echo "Image Tag: ${IMAGE_TAG}"
}

# Execute main function
main
```

### CI/CD Pipeline Configuration

#### GitHub Actions Pipeline
```
name: Deploy to Kubernetes

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Docker images
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./backend/Dockerfile
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          ghcr.io/${{ github.repository }}/backend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: Set up Helm
      uses: azure/setup-helm@v3
      with:
        version: 'latest'

    - name: Configure kubectl
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.KUBE_CONFIG_DATA }}" | base64 -d > ~/.kube/config
        chmod 600 ~/.kube/config

    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install myapp ./helm-charts/myapp \
          --namespace myapp \
          --create-namespace \
          --set backend.image.tag=${{ github.sha }} \
          --set frontend.image.tag=${{ github.sha }} \
          --wait
```

### Monitoring and Alerting Setup
- Prometheus metric collection
- Grafana dashboard configuration
- AlertManager rule definitions
- Log aggregation with Elasticsearch/Fluentd/Kibana
- Application performance monitoring

## Security Considerations
- Secure credential management in automation
- Encrypted communication with clusters
- Minimal required permissions for automation
- Audit logging for deployment activities
- Secure storage of sensitive configuration
- Regular security scanning in pipelines

## Environment Configuration

### Environment-Specific Deployment
```
# Environment variables for deployment
export ENVIRONMENT=${1:-"staging"}  # Default to staging
export CLUSTER_NAME="myapp-${ENVIRONMENT}"
export NAMESPACE="myapp-${ENVIRONMENT}"
export IMAGE_REGISTRY="ghcr.io/myorg/myapp"
export GIT_COMMIT=$(git rev-parse HEAD)
export BUILD_NUMBER=${GITHUB_RUN_NUMBER:-$(date +%s)}

# Environment-specific values
case $ENVIRONMENT in
  "production")
    VALUES_FILE="values-production.yaml"
    REPLICAS_BACKEND=3
    REPLICAS_FRONTEND=3
    ;;
  "staging")
    VALUES_FILE="values-staging.yaml"
    REPLICAS_BACKEND=2
    REPLICAS_FRONTEND=2
    ;;
  *)
    VALUES_FILE="values-development.yaml"
    REPLICAS_BACKEND=1
    REPLICAS_FRONTEND=1
    ;;
esac
```

### Automated Rollback Configuration
```
# Rollback function
rollback_deployment() {
    echo "Initiating rollback..."

    # Get previous release
    PREVIOUS_RELEASE=$(helm list --namespace "${NAMESPACE}" --filter "${APP_NAME}" --max 2 | tail -1 | awk '{print $1}')

    if [ -z "$PREVIOUS_RELEASE" ]; then
        echo "No previous release found for rollback"
        exit 1
    fi

    echo "Rolling back to release: $PREVIOUS_RELEASE"

    # Rollback to previous release
    helm rollback "${APP_NAME}" --namespace "${NAMESPACE}"

    echo "Rollback completed. Waiting for pods to be ready..."

    # Wait for rollback to complete
    kubectl rollout status deployment/"${APP_NAME}"-backend --namespace "${NAMESPACE}" --timeout=300s
    kubectl rollout status deployment/"${APP_NAME}"-frontend --namespace "${NAMESPACE}" --timeout=300s
}
```

## Deployment Integration

### Multi-Environment Setup
- Development environment automation
- Staging environment validation
- Production environment deployment
- Canary release strategies
- Blue-green deployment patterns

### Monitoring Integration
```
# Monitoring configuration
setup_monitoring() {
    echo "Setting up monitoring..."

    # Deploy Prometheus operator if not exists
    kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/latest/download/bundle.yaml

    # Create monitoring resources
    kubectl apply -f monitoring/alertmanager.yaml
    kubectl apply -f monitoring/grafana.yaml
    kubectl apply -f monitoring/prometheus.yaml
    kubectl apply -f monitoring/service-monitors.yaml

    echo "Monitoring setup completed."
}
```

## Troubleshooting Tips

### Deployment Failures
**Symptoms:** Helm deployment fails, pods don't start
**Solutions:**
- Check image pull secrets if using private registries
- Verify image tags exist in registry
- Check resource limits in values.yaml
- Validate Helm chart templates
- Review Kubernetes cluster resources

**Symptoms:** Service not accessible after deployment
**Solutions:**
- Check service configurations
- Verify ingress rules if applicable
- Check network policies
- Validate health check configurations
- Review pod readiness/liveness probes

### CI/CD Pipeline Issues
**Symptoms:** Pipeline fails during deployment
**Solutions:**
- Verify Kubernetes cluster access credentials
- Check Helm repository access
- Validate image registry permissions
- Review environment-specific configurations
- Check resource quotas in target namespace

### Rollback Issues
**Symptoms:** Rollback fails or doesn't restore functionality
**Solutions:**
- Verify previous release exists and is valid
- Check for breaking changes in configuration
- Validate compatibility between releases
- Review database migration compatibility
- Check for persistent volume compatibility

### Debugging Steps
1. Check deployment status: `kubectl get deployments -n <namespace>`
2. Review pod logs: `kubectl logs <pod-name> -n <namespace>`
3. Check events: `kubectl get events -n <namespace>`
4. Validate Helm release: `helm status <release-name> -n <namespace>`
5. Check resource availability in cluster
6. Review pipeline logs for detailed error information

## Best Practices

### Deployment Best Practices
- Implement blue-green or canary deployment strategies
- Use immutable image tags (commit hashes)
- Implement comprehensive health checks
- Set up proper monitoring and alerting
- Use environment-specific configuration
- Implement automated testing in pipelines
- Maintain deployment audit trails

### CI/CD Best Practices
- Use branch-based deployment triggers
- Implement approval gates for production
- Run automated security scans
- Maintain separate environments for testing
- Use infrastructure as code for cluster setup
- Implement automated rollback triggers
- Keep pipeline configurations in version control

### Monitoring Best Practices
- Set up comprehensive application metrics
- Implement custom business metrics
- Configure proper alert thresholds
- Set up dashboard for deployment status
- Monitor resource utilization
- Track deployment success rates
- Log and alert on deployment failures

## Future Improvements

### Advanced Deployment Strategies
- GitOps implementation (ArgoCD, Flux)
- Progressive delivery (Flagger, Istio)
- Automated canary analysis
- Infrastructure as Code (Terraform, CDK8s)
- Multi-cluster deployments
- Disaster recovery automation

### Observability Enhancements
- Distributed tracing setup
- Advanced logging correlation
- Business metric collection
- Predictive alerting
- Automated incident response
- Performance benchmarking

## Testing Checklist

### Deployment Verification
- [ ] Automated script builds Docker images correctly
- [ ] Kubernetes cluster preparation succeeds
- [ ] Helm chart installs without errors
- [ ] All pods become ready
- [ ] Services are accessible
- [ ] Health checks pass
- [ ] Monitoring is properly configured
- [ ] Rollback procedure works correctly