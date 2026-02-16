# Kubernetes Setup Guide - Phase IV Local Deployment

This guide covers deploying the Todo Chatbot application on a local Minikube Kubernetes cluster.

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|-------------|
| Docker Desktop | 4.53+ | [docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Minikube | v1.32+ | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| Helm | v3.14+ | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |
| kubectl | v1.29+ | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |

### Optional Tools (AI-Assisted Operations)

| Tool | Purpose | Installation |
|------|---------|-------------|
| kubectl-ai | Natural language kubectl commands | See [kubectl-ai Setup](#kubectl-ai-setup) |
| kagent | AI-assisted cluster management | See [kagent Setup](#kagent-setup) |
| Docker AI (Gordon) | AI-assisted Docker operations | Docker Desktop 4.53+ Beta features |

### Installation (Ubuntu/WSL2)

```bash
# Install Docker Desktop (Windows) - enable WSL2 integration in settings

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl
```

## Step 1: Build Docker Images

```bash
# From the repository root
cd /path/to/hackathon_todo

# Build both images
docker-compose build

# Or build individually
docker build -t todo-backend ./backend
docker build -t todo-frontend ./frontend
```

### Test with Docker Compose (Pre-Kubernetes)

```bash
# Create a .env file at the repo root with your secrets
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET_KEY=your-jwt-secret
BETTER_AUTH_SECRET=your-better-auth-secret
COHERE_API_KEY=your-cohere-key
COHERE_MODEL=command-nightly
EOF

# Start the application
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Access frontend at http://localhost:3000

# Stop
docker-compose down
```

## Step 2: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --driver=docker --cpus=2 --memory=4096

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

## Step 3: Build Images in Minikube Context

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build images (now they're available inside Minikube)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Verify images exist in Minikube
minikube image ls | grep todo
```

## Step 4: Configure Secrets

```bash
# Create the values override file from the example
cp helm/todo-app/values-minikube.yaml.example helm/todo-app/values-minikube.yaml

# Edit with your actual values
# IMPORTANT: Never commit this file to git!
nano helm/todo-app/values-minikube.yaml
```

## Step 5: Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-app

# Install the Helm chart
helm install todo-app ./helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-minikube.yaml

# Check deployment status
kubectl get pods -n todo-app
kubectl get services -n todo-app

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app -n todo-app --timeout=120s
```

## Step 6: Access the Application

```bash
# Option 1: Use minikube service (opens browser)
minikube service todo-app-frontend -n todo-app

# Option 2: Port forward
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app

# Option 3: Enable ingress (advanced)
minikube addons enable ingress
# Then access via the ingress host configured in values.yaml
```

## Step 7: Verify

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check backend health
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app &
curl http://localhost:8000/health

# View logs
kubectl logs -f deployment/todo-app-backend -n todo-app
kubectl logs -f deployment/todo-app-frontend -n todo-app
```

## Common Operations

### Scale the Application

```bash
# Scale backend to 2 replicas
helm upgrade todo-app ./helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-minikube.yaml \
  --set backend.replicas=2

# Verify
kubectl get pods -n todo-app
```

### Update the Application

```bash
# Rebuild images after code changes
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Restart deployments to pick up new images
kubectl rollout restart deployment/todo-app-backend -n todo-app
kubectl rollout restart deployment/todo-app-frontend -n todo-app
```

### Uninstall

```bash
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
minikube stop
```

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Common issues:
# - ImagePullBackOff: Set imagePullPolicy to Never for local images
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resources with kubectl describe node
```

### Database connection issues

```bash
# Verify DATABASE_URL is set correctly in secrets
kubectl get secret todo-app-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test connectivity from inside a pod
kubectl exec -it deployment/todo-app-backend -n todo-app -- python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL', 'NOT SET')[:30] + '...')
"
```

### Minikube resource issues

```bash
# Check resource usage
minikube dashboard

# Increase resources
minikube stop
minikube start --cpus=4 --memory=8192
```

---

## kubectl-ai Setup

kubectl-ai lets you interact with your Kubernetes cluster using natural language.

### Installation

```bash
# Install via go
go install github.com/sozercan/kubectl-ai@latest

# Or download binary
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64
chmod +x kubectl-ai-linux-amd64
sudo mv kubectl-ai-linux-amd64 /usr/local/bin/kubectl-ai
```

### Configuration

```bash
# Set your OpenAI API key (required)
export OPENAI_API_KEY="your-openai-key"

# Or use environment variable permanently
echo 'export OPENAI_API_KEY="your-openai-key"' >> ~/.bashrc
```

### Example Commands

```bash
# View pods
kubectl-ai "show all pods in the todo-app namespace"

# Check health
kubectl-ai "describe the backend deployment in todo-app namespace"

# Scale
kubectl-ai "scale the backend deployment to 2 replicas in todo-app namespace"

# Debug
kubectl-ai "check why pods are failing in todo-app namespace"

# Logs
kubectl-ai "show recent logs from the backend deployment in todo-app"
```

---

## kagent Setup

kagent provides AI-powered cluster management and analysis.

### Installation

```bash
# Install kagent
pip install kagent

# Or via go
go install github.com/kagent-dev/kagent@latest
```

### Configuration

```bash
# Set API key
export OPENAI_API_KEY="your-openai-key"
```

### Example Commands

```bash
# Cluster health
kagent "analyze the health of the todo-app namespace"

# Resource optimization
kagent "check resource usage of todo-app deployments"

# Troubleshooting
kagent "diagnose why the backend pods are restarting"

# Security
kagent "check for security issues in todo-app namespace"
```

---

## Docker AI (Gordon) Usage

If you have Docker Desktop 4.53+ with Gordon enabled:

```bash
# Get help with Docker operations
docker ai "What can you do?"

# Build optimization
docker ai "optimize the Dockerfile for the backend"

# Troubleshooting
docker ai "why is my container exiting with code 1?"

# Image analysis
docker ai "analyze the todo-backend image for security issues"
```

Enable Gordon: Docker Desktop > Settings > Beta features > Toggle "Docker AI (Gordon)"
