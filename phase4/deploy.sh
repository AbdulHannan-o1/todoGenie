#!/bin/bash

# Deployment script for TodoGenie application to Kubernetes using Helm

set -e  # Exit on any error

echo "Starting TodoGenie Kubernetes deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is required but not installed. Aborting."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "helm is required but not installed. Aborting."
    exit 1
fi

# Start Minikube if not already running
echo "Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start --memory=4096 --cpus=2
else
    echo "Minikube is already running."
fi

# Build Docker images
echo "Building Docker images..."

# Change to backend directory and build
cd ../backend
echo "Building backend image..."
docker build -t todogenie-backend:latest .

# Change to frontend directory and build
cd ../frontend
echo "Building frontend image..."
docker build -t todogenie-frontend:latest .

# Go back to phase4 directory
cd ..

# Load images into Minikube
echo "Loading images into Minikube..."
minikube image load todogenie-backend:latest
minikube image load todogenie-frontend:latest

# Navigate to Helm charts
cd helm-charts

# Install the Helm chart
echo "Installing TodoGenie Helm chart..."
helm upgrade --install todogenie ./todogenie --namespace todogenie --create-namespace

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n todogenie --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n todogenie --timeout=300s

# Display services
echo "Services created:"
kubectl get svc -n todogenie

# Display application access information
echo ""
echo "TodoGenie application deployed successfully!"
echo "Frontend service: $(kubectl get svc todogenie-frontend -n todogenie -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
echo "Backend service: $(kubectl get svc todogenie-backend -n todogenie -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"

# Get minikube service URL if ingress is not enabled
echo ""
echo "To access the frontend via minikube tunnel (in a separate terminal):"
echo "minikube service todogenie-frontend -n todogenie"
echo ""
echo "Or use port forwarding:"
echo "kubectl port-forward -n todogenie svc/todogenie-frontend 3000:3000"

echo ""
echo "Deployment completed!"