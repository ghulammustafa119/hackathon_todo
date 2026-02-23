# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-local-kubernetes-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Health check and deployment validation tests are included as they are essential for cloud-native deployment verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `helm/`, `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify prerequisites and project structure for Kubernetes deployment

- [x] T001 Verify Docker, Minikube, Helm, and kubectl are installed and accessible from CLI
- [x] T002 Create directory structure: `helm/todo-app/templates/`, `docs/`
- [x] T003 [P] Create `helm/todo-app/Chart.yaml` with chart metadata (name: todo-app, version: 0.1.0, appVersion matching project version)

---

## Phase 2: User Story 1 - Containerize Frontend and Backend (Priority: P1)

**Goal**: Build production-ready Docker images for both applications

**Independent Test**: `docker build` both images, `docker-compose up`, verify login + task CRUD + AI chatbot works

### Implementation for User Story 1

- [x] T004 [P] [US1] Create `backend/Dockerfile` with multi-stage build:
  - Stage 1 (`builder`): python:3.11-slim base, copy requirements.txt, pip install
  - Stage 2 (`runtime`): python:3.11-slim base, copy installed packages from builder, copy src/, expose 8000, CMD uvicorn
  - Must handle: .env loading, non-root user, proper PYTHONPATH

- [x] T005 [P] [US1] Create `backend/.dockerignore` excluding: `venv/`, `__pycache__/`, `*.pyc`, `.env`, `todo_app.db`, `*.log`, `.git/`, `tests/`, `specs/`

- [x] T006 [P] [US1] Create `frontend/Dockerfile` with multi-stage build:
  - Stage 1 (`deps`): node:18-alpine base, copy package*.json, npm ci
  - Stage 2 (`builder`): copy source from deps, copy src/, next.config.js, build with `npm run build`
  - Stage 3 (`runner`): node:18-alpine base, copy standalone output from builder, expose 3000, CMD node server.js
  - Must handle: NEXT_PUBLIC env vars at build time, standalone output mode in next.config.js

- [x] T007 [P] [US1] Create `frontend/.dockerignore` excluding: `node_modules/`, `.next/`, `.env.local`, `.git/`, `tests/`

- [x] T008 [US1] Update `frontend/next.config.js` to add `output: 'standalone'` for optimized Docker builds

- [x] T009 [US1] Create `docker-compose.yml` at repository root with:
  - `backend` service: build from `./backend`, ports 8000:8000, environment variables from .env, health check on `/health`
  - `frontend` service: build from `./frontend`, ports 3000:3000, depends_on backend, environment NEXT_PUBLIC_API_URL pointing to backend
  - Shared network for inter-service communication

- [X] T010 [US1] Test: Build both images with `docker-compose build` and verify build succeeds
- [X] T011 [US1] Test: Run `docker-compose up` and verify:
  - Backend health check passes at `http://localhost:8000/health`
  - Frontend loads at `http://localhost:3000`
  - Login, task CRUD, and AI chatbot work end-to-end

**Checkpoint**: At this point, both applications run as Docker containers locally via docker-compose

---

## Phase 3: User Story 2 - Create Helm Charts (Priority: P2)

**Goal**: Package the application as a Helm chart for Kubernetes deployment

**Independent Test**: `helm template` renders valid manifests, `helm lint` passes, `helm install` on Minikube deploys successfully

### Implementation for User Story 2

- [x] T012 [P] [US2] Create `helm/todo-app/values.yaml` with default configuration:
  ```yaml
  backend:
    image: todo-backend:latest
    replicas: 1
    port: 8000
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 500m, memory: 512Mi }
  frontend:
    image: todo-frontend:latest
    replicas: 1
    port: 3000
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 500m, memory: 512Mi }
  ingress:
    enabled: false
  secrets:
    databaseUrl: ""
    secretKey: ""
    cohereApiKey: ""
  ```

- [x] T013 [P] [US2] Create `helm/todo-app/templates/_helpers.tpl` with template helpers:
  - `todo-app.fullname`: generates release-prefixed names
  - `todo-app.labels`: generates standard Kubernetes labels
  - `todo-app.selectorLabels`: generates selector labels

- [x] T014 [US2] Create `helm/todo-app/templates/secrets.yaml`:
  - Kubernetes Secret resource with `stringData` for DATABASE_URL, SECRET_KEY, COHERE_API_KEY
  - Values sourced from `values.yaml` secrets section

- [x] T015 [P] [US2] Create `helm/todo-app/templates/backend-configmap.yaml`:
  - ConfigMap with non-sensitive backend config: HOST, PORT, PYTHONPATH

- [x] T016 [P] [US2] Create `helm/todo-app/templates/frontend-configmap.yaml`:
  - ConfigMap with non-sensitive frontend config: NEXT_PUBLIC_API_URL (pointing to backend ClusterIP service)

- [x] T017 [US2] Create `helm/todo-app/templates/backend-deployment.yaml`:
  - Deployment with configurable replicas from values
  - Container spec with image from values, port 8000
  - Environment from ConfigMap and Secret references
  - Liveness probe: HTTP GET `/health` every 30s, initial delay 10s
  - Readiness probe: HTTP GET `/health` every 10s, initial delay 5s
  - Resource requests and limits from values

- [x] T018 [US2] Create `helm/todo-app/templates/backend-service.yaml`:
  - Service type ClusterIP (internal only)
  - Port 8000 targeting backend pods
  - Selector labels matching backend deployment

- [x] T019 [US2] Create `helm/todo-app/templates/frontend-deployment.yaml`:
  - Deployment with configurable replicas from values
  - Container spec with image from values, port 3000
  - Environment from ConfigMap reference
  - Liveness probe: HTTP GET `/` every 30s, initial delay 15s
  - Readiness probe: HTTP GET `/` every 10s, initial delay 10s
  - Resource requests and limits from values

- [x] T020 [US2] Create `helm/todo-app/templates/frontend-service.yaml`:
  - Service type NodePort (externally accessible via Minikube)
  - Port 3000 targeting frontend pods
  - Selector labels matching frontend deployment

- [x] T021 [P] [US2] Create `helm/todo-app/templates/ingress.yaml`:
  - Conditionally enabled via `ingress.enabled` value
  - Route `/` to frontend service, `/api` to backend service
  - Support for Minikube ingress addon

- [x] T022 [P] [US2] Create `helm/todo-app/templates/NOTES.txt`:
  - Post-install instructions showing how to access the application
  - Commands for `minikube service` or ingress URL

- [x] T023 [US2] Create `helm/todo-app/.helmignore` excluding: `.git/`, `*.swp`, `*.bak`, `*.tmp`

- [X] T024 [US2] Test: Run `helm lint ./helm/todo-app` and verify no errors
- [X] T025 [US2] Test: Run `helm template todo-app ./helm/todo-app` and verify all manifests render correctly

**Checkpoint**: Helm charts are complete and pass linting/template validation

---

## Phase 4: User Story 3 - Deploy on Minikube (Priority: P3)

**Goal**: Deploy the full application on Minikube and verify end-to-end functionality

**Independent Test**: `minikube start`, load Docker images, `helm install`, access application, verify all features work

### Implementation for User Story 3

- [X] T026 [US3] Start Minikube cluster: `minikube start --driver=docker --cpus=2 --memory=4096`

- [X] T027 [US3] Configure Docker to use Minikube's Docker daemon: `eval $(minikube docker-env)` then rebuild images inside Minikube context

- [X] T028 [US3] Create Kubernetes namespace: `kubectl create namespace todo-app`

- [x] T029 [US3] Create a `helm/todo-app/values-minikube.yaml.example` override file with:
  - Actual Neon PostgreSQL DATABASE_URL
  - JWT SECRET_KEY matching the backend .env
  - COHERE_API_KEY for AI chatbot
  - `imagePullPolicy: Never` (using local images)
  - NEXT_PUBLIC_API_URL set to backend service ClusterIP URL

- [X] T030 [US3] Deploy with Helm: `helm install todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-minikube.yaml`

- [X] T031 [US3] Verify deployment: `kubectl get pods -n todo-app` - all pods in Running state

- [X] T032 [US3] Expose frontend: `minikube service todo-app-frontend -n todo-app` and verify application loads in browser

- [X] T033 [US3] Test end-to-end:
  - Login with existing credentials
  - Create a task via the UI
  - Use AI chatbot: "show my tasks"
  - Delete a task
  - Verify all operations succeed

- [X] T034 [US3] Test resilience: Delete a backend pod with `kubectl delete pod` and verify it restarts automatically and recovers

**Checkpoint**: Full application is running on Minikube with all features functional

---

## Phase 5: User Story 4 - AI-Assisted Kubernetes Operations (Priority: P4)

**Goal**: Set up and document kubectl-ai and kagent for AI-assisted cluster management

**Independent Test**: Run kubectl-ai natural language commands and verify they execute correctly

### Implementation for User Story 4

- [x] T035 [P] [US4] Document kubectl-ai installation and setup in `docs/k8s-setup.md`:
  - Installation steps for kubectl-ai
  - Configuration with API key
  - Example commands for todo-app management

- [x] T036 [P] [US4] Document kagent installation and setup in `docs/k8s-setup.md`:
  - Installation steps for kagent
  - Configuration
  - Example commands for cluster health analysis

- [X] T037 [US4] Test kubectl-ai commands:
  - `kubectl-ai "show all pods in todo-app namespace"`
  - `kubectl-ai "describe the backend deployment"`
  - `kubectl-ai "scale backend to 2 replicas"`

- [X] T038 [US4] Test kagent commands:
  - `kagent "analyze cluster health"`
  - `kagent "check resource usage of todo-app"`

**Checkpoint**: kubectl-ai and kagent are installed, documented, and tested

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T039 [P] Create comprehensive `docs/k8s-setup.md` with:
  - Prerequisites (Docker, Minikube, Helm, kubectl)
  - Step-by-step deployment guide
  - Troubleshooting common issues
  - kubectl-ai and kagent usage examples

- [x] T040 [P] Update root `README.md` with Phase IV section:
  - Docker build instructions
  - docker-compose usage
  - Minikube deployment steps
  - Link to detailed k8s-setup.md

- [X] T041 Perform full deployment validation:
  - Clean Minikube start
  - Build images
  - Helm install
  - All features verified
  - Document any issues found

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verify tooling
- **US1 - Containerization (Phase 2)**: Depends on Setup - creates Docker images
- **US2 - Helm Charts (Phase 3)**: Depends on US1 (needs Docker images to reference)
- **US3 - Minikube Deploy (Phase 4)**: Depends on US1 + US2 (needs images and charts)
- **US4 - AI Ops (Phase 5)**: Depends on US3 (needs running cluster to test against)
- **Polish (Phase 6)**: Depends on all user stories complete

### Within Each User Story

- Dockerfiles and .dockerignore can be created in parallel (T004+T005, T006+T007)
- Helm ConfigMaps can be created in parallel (T015+T016)
- Helm Deployment + Service must be sequential (Deployment before Service reference)
- Tests run after implementation within each story

### Parallel Opportunities

- T004, T005, T006, T007: All Dockerfiles and .dockerignore files (different directories)
- T012, T013: values.yaml and _helpers.tpl (independent files)
- T015, T016: Backend and frontend ConfigMaps (independent)
- T021, T022: Ingress and NOTES.txt (independent)
- T035, T036: kubectl-ai and kagent documentation (independent sections)
- T039, T040: Docs and README updates (different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Verify tooling
2. Complete Phase 2: Containerize both apps
3. **STOP and VALIDATE**: `docker-compose up` works end-to-end
4. Proceed to Helm charts

### Incremental Delivery

1. Docker images build and run -> Containers work locally
2. Helm charts created -> Charts lint and template correctly
3. Minikube deployment -> Full stack on Kubernetes
4. AI-assisted ops -> kubectl-ai and kagent operational
5. Documentation -> Complete setup guide

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- `values-minikube.yaml` MUST NOT be committed to git (contains secrets) - add to `.gitignore`
