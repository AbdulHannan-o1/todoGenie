#!/bin/bash
# Build and deploy to Minikube script for Phase5

set -e

echo "🚀 Building and deploying Phase5 to Minikube..."

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📦 Building backend image (phase5)..."
docker build -t todogenie-backend:38 ./phase5/backend

echo "📦 Building frontend image (phase5)..."
docker build -t todogenie-frontend:22 ./phase5/frontend

echo "🔄 Loading images into Minikube..."
minikube image load todogenie-backend:38
minikube image load todogenie-frontend:22

echo "🔄 Updating Minikube deployment..."
minikube kubectl -- set image deployment/todogenie-backend todogenie-backend=todogenie-backend:38 -n todogenie
minikube kubectl -- set image deployment/todogenie-frontend todogenie-frontend=todogenie-frontend:22 -n todogenie

echo "⏳ Waiting for rollout to complete..."
sleep 10
minikube kubectl -- rollout status deployment/todogenie-backend -n todogenie || true
minikube kubectl -- rollout status deployment/todogenie-frontend -n todogenie || true

echo "✅ Deployment complete!"
echo ""
echo "📊 Pod status:"
minikube kubectl -- get pods -n todogenie

echo ""
echo "🔗 Access your app:"
minikube service todogenie-frontend -n todogenie --url 2>/dev/null || echo "Frontend service URL not available"
