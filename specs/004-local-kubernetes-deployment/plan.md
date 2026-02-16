# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-local-kubernetes-deployment` | **Date**: 2026-02-15 | **Spec**: /specs/004-local-kubernetes-deployment/spec.md
**Input**: Feature specification from `/specs/004-local-kubernetes-deployment/spec.md`

## Summary

Deploy the Phase III Todo Chatbot (Next.js frontend + FastAPI backend + AI chatbot with MCP tools) on a local Kubernetes cluster using Docker containerization, Helm charts for package management, and Minikube for local orchestration. The plan includes AI-assisted DevOps using kubectl-ai and kagent for natural language Kubernetes operations.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**: Docker, Docker Compose, Minikube, Helm 3, kubectl, kubectl-ai, kagent
**Storage**: Neon PostgreSQL (external, accessed via DATABASE_URL)
**Testing**: docker build validation, helm template lint, kubectl rollout status, health check endpoints
**Target Platform**: Local Kubernetes (Minikube) on Linux/WSL2
**Project Type**: Web application (containerized frontend + backend)
**Performance Goals**: Pod startup < 60s, health check response < 5s, image build < 5 min
**Constraints**: External database (Neon PostgreSQL), no local database in cluster, multi-stage Docker builds, Helm 3 chart structure
**Scale/Scope**: 1-2 replicas per service on Minikube, configurable via Helm values

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec-Driven Development**: All deployment artifacts originate from Phase IV specification
- [x] **Constitution-First Governance**: Plan aligns with Cloud-Native & Deployment Governance (Phase IV section)
- [x] **Phase Governance Model**: Phase IV focus on Containers + Helm + Minikube
- [x] **Authentication & Security Governance**: JWT secrets managed via Kubernetes Secrets, not hardcoded
- [x] **Stateless System Rule**: Containers are stateless, all state in external Neon PostgreSQL
- [x] **Specification Requirements**: Covers Dockerfiles, Helm charts, Minikube deployment, kubectl-ai/kagent docs

## Project Structure

### Documentation (this feature)

```text
specs/004-local-kubernetes-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (repository root)

```text
# Docker configuration
backend/
├── Dockerfile           # Multi-stage build for FastAPI backend
├── .dockerignore        # Exclude venv, __pycache__, .env, etc.
└── ...                  # Existing backend code (unchanged)

frontend/
├── Dockerfile           # Multi-stage build for Next.js frontend
├── .dockerignore        # Exclude node_modules, .next, etc.
└── ...                  # Existing frontend code (unchanged)

docker-compose.yml       # Local multi-container orchestration (root level)

# Helm charts
helm/
└── todo-app/
    ├── Chart.yaml        # Chart metadata (name, version, dependencies)
    ├── values.yaml       # Default configuration values
    ├── templates/
    │   ├── _helpers.tpl           # Template helper functions
    │   ├── backend-deployment.yaml
    │   ├── backend-service.yaml
    │   ├── backend-configmap.yaml
    │   ├── frontend-deployment.yaml
    │   ├── frontend-service.yaml
    │   ├── frontend-configmap.yaml
    │   ├── secrets.yaml
    │   ├── ingress.yaml
    │   └── NOTES.txt              # Post-install instructions
    └── .helmignore

# Documentation
docs/
└── k8s-setup.md          # Setup guide for Minikube, kubectl-ai, kagent
```

**Structure Decision**: Single Helm chart (`todo-app`) containing both frontend and backend as sub-components. This simplifies deployment as a single `helm install` deploys the full stack. Helm values control per-component configuration (replicas, resources, environment). Docker Compose is provided for pre-Kubernetes local testing.

## Architecture Overview

```
                        ┌──────────────────────────────────────────────┐
                        │              Minikube Cluster                │
                        │                                              │
  ┌─────────┐           │  ┌──────────────┐    ┌──────────────┐       │
  │ Browser  │──────────┼─▶│  Frontend    │───▶│  Backend     │       │
  │          │           │  │  Service     │    │  Service     │       │
  └─────────┘           │  │  (NodePort)  │    │  (ClusterIP) │       │
                        │  └──────┬───────┘    └──────┬───────┘       │
                        │         │                    │               │
                        │  ┌──────▼───────┐    ┌──────▼───────┐       │
                        │  │  Frontend    │    │  Backend     │       │
                        │  │  Deployment  │    │  Deployment  │       │
                        │  │  (1-2 pods)  │    │  (1-2 pods)  │       │
                        │  └──────────────┘    └──────────────┘       │
                        │                                              │
                        │  ┌──────────────┐    ┌──────────────┐       │
                        │  │  ConfigMaps  │    │  Secrets     │       │
                        │  │  (env vars)  │    │  (DB URL,    │       │
                        │  │              │    │   JWT key)   │       │
                        │  └──────────────┘    └──────────────┘       │
                        └──────────────────────────────────────────────┘
                                                     │
                                                     ▼
                                            ┌──────────────┐
                                            │  Neon        │
                                            │  PostgreSQL  │
                                            │  (External)  │
                                            └──────────────┘
```

## Key Design Decisions

### 1. Single Helm Chart vs Multiple Charts
**Decision**: Single umbrella chart `todo-app` with sub-templates for frontend and backend.
**Rationale**: Simpler for local Minikube deployment. Phase V may split into sub-charts for independent cloud scaling.
**Trade-off**: Less granular versioning, but acceptable for Phase IV scope.

### 2. External Database (No In-Cluster DB)
**Decision**: Continue using Neon PostgreSQL as external database.
**Rationale**: Constitution mandates Neon PostgreSQL. Running PostgreSQL in Minikube adds complexity and contradicts the external database constraint.
**Trade-off**: Requires network access from Minikube to Neon PostgreSQL (internet connectivity required).

### 3. Multi-Stage Docker Builds
**Decision**: Use multi-stage builds for both frontend and backend.
**Rationale**: Reduces image size by excluding build tools and dev dependencies from final image.
**Backend stages**: (1) Install dependencies → (2) Runtime with only production packages.
**Frontend stages**: (1) Install + build → (2) Runtime with only built artifacts and Next.js standalone output.

### 4. Service Exposure Strategy
**Decision**: Frontend exposed via NodePort (or `minikube service`), backend as ClusterIP (internal only).
**Rationale**: Frontend is the entry point for users. Backend is accessed only by frontend within the cluster. The frontend Next.js app proxies API calls to the backend service.

### 5. Environment Variable Management
**Decision**: Sensitive values (DATABASE_URL, SECRET_KEY, API keys) in Kubernetes Secrets. Non-sensitive values (NEXT_PUBLIC_API_URL, PORT) in ConfigMaps.
**Rationale**: Follows Kubernetes security best practices. Secrets are base64 encoded and can be encrypted at rest.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
