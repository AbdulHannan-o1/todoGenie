# Quickstart Guide: Kubernetes Deployment for TodoGenie

## Prerequisites

- Docker Desktop running
- Minikube installed and running
- Helm 3 installed
- kubectl installed and configured

## Setup Instructions

### 1. Start Minikube
```bash
minikube start --memory=4096 --cpus=2
```

### 2. Clone the Repository
```bash
git clone [repository-url]
cd todogenie
```

### 3. Navigate to Phase 4
```bash
cd phase4
```

## Deployment Steps

### 1. Build Docker Images
```bash
# Build backend image
cd backend
docker build -t todogenie-backend:latest .
cd ..

# Build frontend image
cd frontend
docker build -t todogenie-frontend:latest .
cd ..
```

### 2. Load Images into Minikube
```bash
# Load images into minikube
minikube image load todogenie-backend:latest
minikube image load todogenie-frontend:latest
```

### 3. Deploy Using Helm
```bash
# Navigate to helm charts
cd helm-charts

# Install the chart
helm install todogenie ./todogenie --namespace todogenie --create-namespace
```

### 4. Verify Deployment
```bash
# Check pods
kubectl get pods -n todogenie

# Check services
kubectl get svc -n todogenie

# Get application URL
minikube service frontend-service -n todogenie --url
```

## Accessing the Application

1. Get the frontend URL:
```bash
minikube service frontend-service -n todogenie
```

2. Access the application in your browser using the provided URL

## Troubleshooting

### Common Issues

1. **Images not found**: Ensure images are loaded into minikube with `minikube image load`
2. **Insufficient resources**: Increase minikube resources with `minikube delete` and restart with higher limits
3. **Service not accessible**: Check if all pods are running with `kubectl get pods -n todogenie`

### Useful Commands

```bash
# View logs
kubectl logs -l app=backend -n todogenie
kubectl logs -l app=frontend -n todogenie

# Port forward for debugging
kubectl port-forward -n todogenie svc/frontend-service 3000:3000
kubectl port-forward -n todogenie svc/backend-service 8000:8000

# Uninstall the release
helm uninstall todogenie -n todogenie
```

## Cleanup

```bash
# Uninstall the Helm release
helm uninstall todogenie -n todogenie

# Optionally delete namespace
kubectl delete namespace todogenie

# Stop minikube
minikube stop
```