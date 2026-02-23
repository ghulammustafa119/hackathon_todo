
# Todo Evolution Project

A 5-phase evolution of a Todo List Manager, demonstrating Spec-Driven Development (SDD) principles with stateless architecture, AI integration, and cloud-native event-driven architecture.

## Project Overview

This project implements a Todo List Manager that evolves through 5 phases, from a simple console application to a cloud-native, event-driven system. Each phase builds upon the previous while maintaining strict adherence to stateless architecture principles.

### Live Deployments

| Service | URL |
|---------|-----|
| Frontend (Vercel) | https://hackathon-todo-beryl.vercel.app |
| Backend (HF Spaces) | https://ghulammustafabhutto-todo-backend.hf.space |

### Phases

| Phase | Description | Status |
|-------|-------------|--------|
| I | In-Memory Console Application | Complete |
| II | Full-Stack Web Application with Authentication | Complete |
| III | AI Chatbot Integration (Stateless) | Complete |
| IV | Local Kubernetes Deployment (Docker, Minikube, Helm) | Complete |
| V | Cloud-Native Event-Driven Architecture | Complete |

## Phase I - In-Memory Console Todo App

A console-based Todo List Manager with in-memory storage.

### Features

- Add new tasks with title and optional description
- List all tasks with completion status
- Update task title and description
- Delete tasks
- Mark tasks as complete/incomplete
- Menu-driven interface with input validation

### Running

```bash
python todo_console/main.py
```

## Phase II - Full-Stack Web Application with Authentication

A full-stack web application with persistent data storage and user authentication.

### Features

- User authentication via Better Auth (email/password signup & login)
- Better Auth JWT plugin with EdDSA (Ed25519) token signing
- Backend verifies tokens via JWKS endpoint (EdDSA) with HS256 fallback
- User-scoped task access control
- REST API with JSON data exchange
- Responsive web interface using Next.js
- PostgreSQL database (Neon) with SQLModel ORM

### Architecture

- **Backend**: FastAPI + SQLModel ORM + Neon PostgreSQL
- **Frontend**: Next.js with Better Auth client + httpOnly cookie sessions
- **Auth**: Better Auth (JWKS/EdDSA) → FastAPI JWT verification (PyJWT + python-jose fallback)
- **Security**: httpOnly cookies, security headers middleware, CORS whitelist
- **Stateless**: No server-side session storage

## Phase III - AI Chatbot Integration (Stateless)

Natural language interface for managing tasks using Cohere AI and MCP tools.

### Features

- Natural language task CRUD via chat interface (e.g., "buy a book", "show my tasks")
- Cohere Agent for intent detection and tool orchestration
- Keyword-based fallback when Cohere fails to return structured JSON
- MCP tools: create_task, list_tasks, update_task, delete_task, complete_task
- MCP server uses JWKS-aware token verification (EdDSA + HS256)
- Numbered task reference support (e.g., "mark task 6 as done")
- JWT token propagation: frontend -> agent -> MCP server -> backend

## Phase IV - Local Kubernetes Deployment

Containerized deployment on Minikube with Helm charts.

### Features

- Multi-stage Docker builds for frontend and backend
- Docker Compose for local multi-container testing
- Helm charts (Deployments, Services, ConfigMaps, Secrets, Ingress)
- Health check probes (liveness and readiness)

### Quick Start

```bash
docker-compose build && docker-compose up -d
# Frontend: http://localhost:3000 | Backend: http://localhost:8000
```

## Phase V - Cloud-Native Event-Driven Architecture

Advanced cloud-native architecture with Kafka event streaming, Dapr sidecars, and event-driven microservices.

### Architecture Overview

```
                    +------------------+
                    |   Next.js        |
                    |   Frontend       |
                    |   (Vercel)       |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   FastAPI        |
                    |   Backend        |    Dapr Sidecar
                    |   (HF Spaces)    +<---------------+
                    +--------+---------+                |
                             |                          |
              +--------------+--------------+           |
              |              |              |    +------v------+
     +--------v--+   +------v----+  +------v-+  |  Redpanda   |
     | Reminder  |   | Recurrence|  | Audit  |  |  (Kafka)    |
     | Service   |   | Service   |  | Service|  +-------------+
     | :8001     |   | :8002     |  | :8003  |
     +-----------+   +-----------+  +--------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    |  Neon PostgreSQL  |
                    +------------------+
```

### User Stories Implemented

#### US1: Task Priorities, Tags, and Organization
- Assign priorities (low/medium/high/urgent) to tasks
- Add/remove tags for task categorization
- Filter tasks by priority, status, and tag
- Sort tasks by date, priority, due date, or title
- Full-text search across task titles, descriptions, and tags
- Priority badges and tag chips in the UI

#### US2: Due Dates and Reminders
- Set due dates with datetime picker
- Overdue task highlighting (red border indicator)
- In-app notification bell with reminder alerts
- Reminder lead time configuration (minutes before due)
- Notifications API (GET/PATCH for read status)

#### US3: Event-Driven Task Operations
- All CRUD operations emit CloudEvents v1.0 events
- Transactional outbox pattern for reliable delivery
- Events: task.created, task.updated, task.deleted, task.completed
- Previous state capture for update events
- Retry with exponential backoff for Dapr publishing

#### US4: Recurring Tasks
- Recurrence rules: daily, weekly, monthly, custom cron
- Recurrence microservice subscribes to task.completed events
- Auto-creates next task instance with calculated due date
- Recurrence parent tracking (recurrence_parent_id)
- Recurring task indicator icon in the UI

#### US5: AI Chatbot with Conversation History
- Session timeout (30-minute expiry)
- Sliding window context (last 20 messages, 4000 token budget)
- 4 new MCP tools: search_tasks, set_priority, add_tags, set_due_date
- Multi-turn conversation with pronoun resolution
- Task reference context injection

#### US6: Cloud Kubernetes Deployment (DOKS)
- Helm charts for all microservices with Dapr sidecar annotations
- Dapr pub/sub component (Redpanda/Kafka)
- Dapr state store component (PostgreSQL)
- HPA (Horizontal Pod Autoscaler) for backend and frontend
- DOKS-specific values overlay (values-doks.yaml)

#### US7: Audit Trail Service
- Immutable audit log of all task operations
- Idempotency check via event_id unique constraint
- Admin query API (filter by user, task, operation)
- PostgreSQL-backed persistent audit entries

### New Microservices

| Service | Port | Purpose |
|---------|------|---------|
| Reminder | 8001 | Schedules and fires task reminders via Dapr state store |
| Recurrence | 8002 | Auto-creates next task instance when recurring task completes |
| Audit | 8003 | Immutable event log with idempotency and admin query API |

### New Backend Models

| Model | Table | Purpose |
|-------|-------|---------|
| TaskEvent | taskevent | CloudEvents-compatible task event log |
| OutboxEvent | outboxevent | Transactional outbox for reliable publishing |
| Tag | tag | User-scoped tags for task organization |
| TaskTag | tasktag | Many-to-many junction for tasks and tags |
| AuditEntry | audit_entries | Immutable audit trail entries |
| ReminderSchedule | reminder_schedule | Scheduled reminder tracking |

### New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks?priority=&status=&tag=&search=&sort_by=&sort_order= | Filtered/sorted task list |
| GET | /api/{user_id}/tags | List user's tags |
| GET | /api/{user_id}/notifications | Get pending notifications |
| PATCH | /api/{user_id}/notifications/{id}/read | Dismiss notification |
| GET | /dapr/subscribe | Dapr subscription registration |
| POST | /events/task-commands | Handle recurrence task creation commands |

### Infrastructure

| Component | Purpose |
|-----------|---------|
| Redpanda | Kafka-compatible event streaming (single node, 0.5 CPU / 1 GiB) |
| Dapr | Sidecar for pub/sub, state store, service invocation |
| Neon PostgreSQL | Managed database for all services |

### Project Structure (Phase V additions)

```
hackathon_todo/
├── services/
│   ├── reminder/           # Reminder microservice
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── recurrence/         # Recurrence microservice
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── audit/              # Audit microservice
│       ├── main.py
│       ├── Dockerfile
│       └── requirements.txt
├── dapr/
│   └── components/
│       ├── pubsub.yaml     # Redpanda Kafka pub/sub
│       └── statestore.yaml # PostgreSQL state store
├── helm/todo-app/
│   ├── templates/
│   │   ├── dapr-pubsub.yaml
│   │   ├── dapr-statestore.yaml
│   │   ├── reminder-deployment.yaml
│   │   ├── recurrence-deployment.yaml
│   │   ├── audit-deployment.yaml
│   │   └── hpa.yaml
│   ├── values.yaml
│   └── values-doks.yaml
├── backend/
│   ├── src/models/
│   │   ├── event.py        # TaskEvent, OutboxEvent
│   │   ├── tag.py          # Tag, TaskTag
│   │   ├── audit.py        # AuditEntry
│   │   └── reminder.py     # ReminderSchedule
│   ├── src/services/
│   │   ├── event_publisher.py  # Dapr event publisher with retry
│   │   └── task_service.py     # Extended with events, tags, filters
│   ├── src/api/
│   │   ├── tags.py         # Tag listing endpoint
│   │   └── notifications.py# Reminder notifications
│   └── src/ai_chatbot/tools/
│       ├── search_tasks_tool.py
│       ├── set_priority_tool.py
│       ├── add_tags_tool.py
│       └── set_due_date_tool.py
└── frontend/src/
    ├── components/tasks/
    │   ├── task-filters.tsx     # Sort/filter/search controls
    │   └── notification-bell.tsx# In-app notifications
    └── types/
        └── task.ts             # Extended with priority, tags, due_date, recurrence
```

### Local Development with All Services

```bash
# Start everything (backend, frontend, Redpanda, reminder, recurrence, audit)
docker-compose up -d

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Reminder: http://localhost:8001
# Recurrence: http://localhost:8002
# Audit:    http://localhost:8003
```

### DOKS Deployment

```bash
# Install Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm install dapr dapr/dapr --namespace dapr-system --create-namespace

# Install Redpanda
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda --namespace redpanda --create-namespace \
  --set resources.cpu.cores=0.5 --set resources.memory.container.max=1Gi

# Deploy application
helm install todo-app ./helm/todo-app -f helm/todo-app/values-doks.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.secretKey="$JWT_SECRET_KEY" \
  --set secrets.cohereApiKey="$COHERE_API_KEY"
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, SQLModel |
| Database | Neon PostgreSQL |
| AI | Cohere API, MCP Tools |
| Events | Redpanda (Kafka), CloudEvents v1.0 |
| Orchestration | Dapr, Kubernetes, Helm |
| Deployment | Vercel (frontend), HF Spaces (backend), DOKS (K8s) |

## Governance

All code follows Spec-Driven Development principles:
1. Features start with specification (`/sp.specify`)
2. Planning before implementation (`/sp.plan`)
3. Tasks generated from plan (`/sp.tasks`)
4. Implementation via `/sp.implement`

---

**Built with Spec-Driven Development | Constitution-first governance | Python 3.11+ | Cohere AI | Event-Driven Architecture**
