# Implementation Plan: Phase V – Cloud-Native Event-Driven Architecture

**Branch**: `005-cloud-native-event-driven` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-cloud-native-event-driven/spec.md`

## Summary

Extend the Todo application with advanced task features (priorities, tags, due dates, recurring tasks, reminders), event-driven microservices (reminder, recurrence, audit) using Kafka/Dapr, multi-turn AI chatbot with conversation history, and cloud deployment on DigitalOcean Kubernetes (DOKS).

## Technical Context

**Language/Version**: Python 3.11+ (backend, microservices), TypeScript/JavaScript (frontend Next.js 14)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK, httpx, croniter, Cohere API, Redpanda (Kafka-compatible)
**Storage**: Neon PostgreSQL (existing), Dapr state store (microservices), Redpanda (event streaming)
**Testing**: pytest (backend), manual E2E testing
**Target Platform**: DigitalOcean Kubernetes (DOKS) - 3x s-2vcpu-4gb nodes
**Project Type**: Web application (frontend + backend + microservices)
**Performance Goals**: <2s task operations, <5s event delivery, <60s pod recovery
**Constraints**: ~$90/month cloud budget, Constitution mandates Kafka + Dapr
**Scale/Scope**: 100 concurrent users, 7 user stories, 20 functional requirements

## Constitution Check

*GATE: All checks PASS*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-Driven Development | ✅ PASS | Spec created before plan; all features specified |
| Kafka MUST be used | ✅ PASS | Redpanda (Kafka-compatible) for event streaming |
| Dapr MUST be used for Pub/Sub, State, Bindings, Service invocation | ✅ PASS | Dapr sidecar model with pub/sub, state store, service invocation |
| Intermediate features (priorities, tags, search, filter, sort) | ✅ PASS | User Story 1, FR-001 through FR-005 |
| Advanced features (recurring, due dates, reminders) | ✅ PASS | User Stories 2, 4; FR-006 through FR-012 |
| Decoupled services for reminders and recurrence | ✅ PASS | 3 microservices: reminder, recurrence, audit |
| Event schemas MUST be versioned | ✅ PASS | CloudEvents v1.0 with schema_version field |
| Services communicate via events, not direct calls | ✅ PASS | Dapr pub/sub; command event pattern for recurrence |
| Stateless System Rule | ✅ PASS | All state in PostgreSQL/Dapr state store |
| Authentication mandatory | ✅ PASS | JWT auth preserved from Phase II |
| Cloud deployment (DOKS/GKE/AKS) | ✅ PASS | DOKS as primary target |

## Project Structure

### Documentation (this feature)

```text
specs/005-cloud-native-event-driven/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── task-events.yaml
│   └── api-extensions.yaml
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Extended: priority, tags, due_date, recurrence
│   │   ├── tag.py               # NEW: Tag + TaskTag models
│   │   ├── conversation.py      # Extended: session timeout, task references
│   │   ├── audit.py             # NEW: AuditEntry model
│   │   ├── reminder.py          # NEW: ReminderSchedule model
│   │   ├── event.py             # NEW: TaskEvent, OutboxEvent models
│   │   └── user.py              # Existing
│   ├── services/
│   │   ├── task_service.py      # Extended: filtering, sorting, search, event publishing
│   │   ├── event_publisher.py   # NEW: Dapr pub/sub integration
│   │   └── cohere_client.py     # Existing
│   ├── api/
│   │   ├── tasks.py             # Extended: query params for filter/sort/search
│   │   ├── tags.py              # NEW: tag endpoints
│   │   ├── notifications.py     # NEW: reminder notification endpoints
│   │   ├── audit.py             # NEW: admin audit log endpoint
│   │   ├── auth.py              # Existing
│   │   └── ai_chat.py           # Extended: session_id support
│   ├── ai_chatbot/
│   │   ├── tools/               # Extended: 5 new MCP tools
│   │   │   ├── search_tasks_tool.py    # NEW
│   │   │   ├── set_priority_tool.py    # NEW
│   │   │   ├── add_tags_tool.py        # NEW
│   │   │   ├── set_due_date_tool.py    # NEW
│   │   │   └── set_recurring_tool.py   # NEW
│   │   └── services/
│   │       └── conversation_service.py # Extended: session timeout, context window
│   └── database/
│       └── session.py           # Existing (already handles PostgreSQL)

services/                        # NEW: microservices directory
├── reminder/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py                  # FastAPI app with Dapr subscription
├── recurrence/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
└── audit/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── task-form.tsx        # Extended: priority, tags, due date fields
│   │   │   ├── task-list.tsx        # Extended: sort, filter, search UI
│   │   │   ├── task-filters.tsx     # NEW: filter/sort controls
│   │   │   └── notification-bell.tsx # NEW: reminder notifications
│   │   └── chat/
│   │       └── chat-interface.tsx   # Extended: session management
│   └── types/
│       └── task.ts              # Extended: new fields

helm/todo-app/
├── templates/
│   ├── reminder-deployment.yaml     # NEW
│   ├── reminder-service.yaml        # NEW
│   ├── recurrence-deployment.yaml   # NEW
│   ├── recurrence-service.yaml      # NEW
│   ├── audit-deployment.yaml        # NEW
│   ├── audit-service.yaml           # NEW
│   ├── dapr-pubsub.yaml            # NEW: Dapr Kafka component
│   ├── dapr-statestore.yaml        # NEW: Dapr state store component
│   └── redpanda-*.yaml             # NEW: Redpanda deployment
├── values.yaml                      # Extended with microservice configs
└── values-doks.yaml                 # NEW: DOKS-specific values
```

**Structure Decision**: Microservices live under `services/` at the repo root (separate from `backend/`). Each has its own Dockerfile and requirements.txt. Shared event schemas are in `backend/src/models/event.py` and copied to each microservice during Docker build.

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Frontend    │────▶│  Backend     │────▶│  Neon PostgreSQL  │
│  (Next.js)   │     │  (FastAPI)   │     │  (Tasks, Users,   │
│  Vercel/K8s  │     │  + Dapr      │     │   Conversations)  │
└─────────────┘     │  Sidecar     │     └──────────────────┘
                    └──────┬───────┘
                           │ publish events
                    ┌──────▼───────┐
                    │  Redpanda    │
                    │  (Kafka)     │
                    │  tasks topic │
                    └──┬────┬───┬──┘
                       │    │   │
              ┌────────┘    │   └────────┐
              ▼             ▼            ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────┐
     │  Reminder    │ │Recurrence│ │  Audit   │
     │  Service     │ │ Service  │ │  Service │
     │  + Dapr      │ │ + Dapr   │ │ + Dapr   │
     └──────────────┘ └──────────┘ └──────────┘
```

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Redpanda over Strimzi | 1/3 resource usage, Kafka-compatible, fits $90/mo budget |
| Dapr pub/sub for all inter-service comms | Constitution mandate; standard API abstraction |
| Single `tasks` topic with event_type routing | Simpler than per-type topics for small system |
| Command event pattern for recurrence | Backend remains single authority for task creation |
| PostgreSQL for conversation history (not Redis) | Already have it; sufficient at 100-user scale |
| Sliding window (20 msgs) for chatbot context | Balances context quality and token cost |
| Direct publish + retry (not outbox) | Pragmatic for Phase V; outbox documented as enhancement |
| DOKS 3x s-2vcpu-4gb ($72/mo) | 3x headroom over workload, budget-conscious |

## Complexity Tracking

> No Constitution violations. All complexity is justified by spec requirements and Constitution mandates.
