# Tasks: Phase V – Cloud-Native Event-Driven Architecture

**Input**: Design documents from `/specs/005-cloud-native-event-driven/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1–US7)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: New dependencies, Dapr local config, microservice scaffolding

- [ ] T001 Add new Python dependencies to backend/requirements.txt (httpx, croniter, dapr)
- [ ] T002 [P] Create shared event schema module in backend/src/models/event.py (TaskEvent, OutboxEvent models per data-model.md)
- [ ] T003 [P] Create Dapr components directory at dapr/components/ with pubsub.yaml (Redpanda) and statestore.yaml (PostgreSQL)
- [ ] T004 [P] Scaffold reminder microservice directory: services/reminder/ with main.py, requirements.txt, Dockerfile
- [ ] T005 [P] Scaffold recurrence microservice directory: services/recurrence/ with main.py, requirements.txt, Dockerfile
- [ ] T006 [P] Scaffold audit microservice directory: services/audit/ with main.py, requirements.txt, Dockerfile
- [ ] T007 Update frontend/src/types/task.ts to add priority, tags, due_date, reminder_lead_time, recurrence_rule, recurrence_parent_id fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Extend Task model with new fields (priority, due_date, reminder_lead_time, recurrence_rule, recurrence_parent_id) in backend/src/models/task.py
- [ ] T009 [P] Create Tag and TaskTag models in backend/src/models/tag.py per data-model.md
- [ ] T010 [P] Create AuditEntry model in backend/src/models/audit.py per data-model.md
- [ ] T011 [P] Create ReminderSchedule model in backend/src/models/reminder.py per data-model.md
- [ ] T012 Create Dapr event publisher service in backend/src/services/event_publisher.py (publish to Dapr sidecar HTTP API at localhost:3500)
- [ ] T013 Extend ConversationSession model (replaces ConversationHistory) with session timeout and message_count in backend/src/models/conversation.py per data-model.md
- [ ] T014 Extend ConversationMessage model with task_references, token_count, tool_calls fields in backend/src/models/conversation.py
- [ ] T015 Run database migration: ensure all new models/tables are created on Neon PostgreSQL (SQLModel.metadata.create_all)
- [ ] T016 Add full-text search indexes on task title and description in Neon PostgreSQL per data-model.md indexes section

**Checkpoint**: Foundation ready – all models exist, event publisher ready, DB migrated

---

## Phase 3: User Story 1 – Task Priorities, Tags, and Organization (Priority: P1) MVP

**Goal**: Users can assign priorities and tags, sort/filter/search tasks

**Independent Test**: Create tasks with priorities and tags, verify sort/filter/search work correctly via API and frontend

### Implementation for User Story 1

- [ ] T017 [US1] Extend TaskService with priority and tag support in backend/src/services/task_service.py (create/update tasks with priority, manage tags)
- [ ] T018 [US1] Add tag CRUD operations to TaskService in backend/src/services/task_service.py (add_tags, remove_tags, get_user_tags)
- [ ] T019 [US1] Extend GET /api/{user_id}/tasks with query params (sort_by, sort_order, priority, tag, status, search) in backend/src/api/tasks.py
- [ ] T020 [US1] Implement full-text search in TaskService using PostgreSQL tsvector in backend/src/services/task_service.py
- [ ] T021 [P] [US1] Create tag listing endpoint GET /api/{user_id}/tags in backend/src/api/tags.py
- [ ] T022 [US1] Extend POST/PUT /api/{user_id}/tasks to accept priority and tags in backend/src/api/tasks.py
- [ ] T023 [P] [US1] Update task-form.tsx with priority dropdown and tag input in frontend/src/components/tasks/task-form.tsx
- [ ] T024 [P] [US1] Create task-filters.tsx component with sort/filter/search controls in frontend/src/components/tasks/task-filters.tsx
- [ ] T025 [US1] Update task-list.tsx to display priority badges, tag chips, and integrate filters in frontend/src/components/tasks/task-list.tsx
- [ ] T026 [US1] Update task-update-form.tsx to support editing priority and tags in frontend/src/components/tasks/task-update-form.tsx

**Checkpoint**: Users can create/edit tasks with priorities and tags, sort, filter, and search. MVP deliverable.

---

## Phase 4: User Story 2 – Due Dates and Reminders (Priority: P1)

**Goal**: Users can set due dates, see overdue indicators, and receive in-app reminders

**Independent Test**: Create task with due date, verify overdue highlighting, verify reminder notification fires

### Implementation for User Story 2

- [ ] T027 [US2] Extend TaskService to handle due_date and reminder_lead_time on create/update in backend/src/services/task_service.py
- [ ] T028 [US2] Extend task API endpoints to accept due_date and reminder_lead_time in backend/src/api/tasks.py
- [ ] T029 [P] [US2] Create notifications API endpoint GET /api/{user_id}/notifications in backend/src/api/notifications.py
- [ ] T030 [P] [US2] Create PATCH /api/{user_id}/notifications/{id}/read endpoint in backend/src/api/notifications.py
- [ ] T031 [US2] Implement Reminder Service event handler in services/reminder/main.py (subscribe to tasks topic, schedule/cancel reminders via Dapr state store)
- [ ] T032 [US2] Implement Reminder Service scheduler loop in services/reminder/main.py (check pending reminders every 30s, publish reminder.fired events)
- [ ] T033 [P] [US2] Update task-form.tsx to add due date/time picker and reminder lead time input in frontend/src/components/tasks/task-form.tsx
- [ ] T034 [P] [US2] Create notification-bell.tsx component for in-app reminder notifications in frontend/src/components/tasks/notification-bell.tsx
- [ ] T035 [US2] Update task-list.tsx to show overdue highlighting (red border for past due_date) in frontend/src/components/tasks/task-list.tsx
- [ ] T036 [US2] Update dashboard/page.tsx to include notification bell component in frontend/src/app/dashboard/page.tsx

**Checkpoint**: Due dates with overdue indicators working. Reminder service fires notifications.

---

## Phase 5: User Story 3 – Event-Driven Task Operations (Priority: P2)

**Goal**: All task CRUD operations emit Kafka events via Dapr pub/sub

**Independent Test**: Perform task operations and verify events appear on Redpanda tasks topic

**Depends on**: US1 and US2 (task model must have all fields before events carry them)

### Implementation for User Story 3

- [ ] T037 [US3] Integrate event_publisher.py into TaskService: publish task.created event after task creation in backend/src/services/task_service.py
- [ ] T038 [US3] Publish task.updated event (with previous_state) after task update in backend/src/services/task_service.py
- [ ] T039 [US3] Publish task.deleted event after task deletion in backend/src/services/task_service.py
- [ ] T040 [US3] Publish task.completed event after task completion toggle in backend/src/services/task_service.py
- [ ] T041 [US3] Add CloudEvents envelope (specversion, type, source, id, time) to event publisher in backend/src/services/event_publisher.py
- [ ] T042 [US3] Add retry logic with exponential backoff to event publisher in backend/src/services/event_publisher.py
- [ ] T043 [US3] Update backend Dockerfile to include Dapr sidecar annotations in backend/Dockerfile and helm/todo-app/templates/backend-deployment.yaml

**Checkpoint**: Every task operation emits a versioned CloudEvents event to Redpanda via Dapr.

---

## Phase 6: User Story 4 – Recurring Tasks (Priority: P2)

**Goal**: Users can set recurrence rules; completed recurring tasks auto-create next instance

**Independent Test**: Create daily recurring task, complete it, verify new instance created

**Depends on**: US3 (needs task.completed events flowing)

### Implementation for User Story 4

- [ ] T044 [US4] Extend TaskService to handle recurrence_rule and recurrence_parent_id on create/update in backend/src/services/task_service.py
- [ ] T045 [US4] Extend task API to accept recurrence_rule parameter in backend/src/api/tasks.py
- [ ] T046 [US4] Implement Recurrence Service event handler in services/recurrence/main.py (subscribe to tasks topic, listen for task.completed with recurrence_rule)
- [ ] T047 [US4] Implement next-due-date calculation using croniter in services/recurrence/main.py (daily/weekly/monthly/cron)
- [ ] T048 [US4] Publish task.create.requested command event from Recurrence Service to task-commands topic in services/recurrence/main.py
- [ ] T049 [US4] Subscribe backend to task-commands topic and create new task from command event in backend/src/api/tasks.py or backend/src/services/task_service.py
- [ ] T050 [P] [US4] Update task-form.tsx to add recurrence selector (daily/weekly/monthly/custom) in frontend/src/components/tasks/task-form.tsx
- [ ] T051 [US4] Update task-list.tsx to show recurring task indicator icon in frontend/src/components/tasks/task-list.tsx

**Checkpoint**: Recurring tasks auto-regenerate on completion via event-driven recurrence service.

---

## Phase 7: User Story 5 – AI Chatbot with Conversation History (Priority: P2)

**Goal**: Multi-turn chatbot with session management and pronoun resolution

**Independent Test**: Send "add task meeting" then "set it to high priority" – verify context maintained

### Implementation for User Story 5

- [ ] T052 [US5] Extend ConversationService with session timeout logic (30-min expiry) in backend/src/ai_chatbot/services/conversation_service.py
- [ ] T053 [US5] Implement sliding window context builder (last 20 messages, 4000 token budget) in backend/src/ai_chatbot/services/conversation_service.py
- [ ] T054 [US5] Inject task reference context into system prompt for pronoun resolution in backend/src/ai_chatbot/agents/cohere_agent.py
- [ ] T055 [US5] Extend chat API to accept/return session_id in backend/src/api/ai_chat.py
- [ ] T056 [US5] Pass conversation history to Cohere API for multi-turn context in backend/src/ai_chatbot/agents/cohere_agent.py
- [ ] T057 [P] [US5] Create search_tasks MCP tool in backend/src/ai_chatbot/tools/search_tasks_tool.py
- [ ] T058 [P] [US5] Create set_priority MCP tool in backend/src/ai_chatbot/tools/set_priority_tool.py
- [ ] T059 [P] [US5] Create add_tags MCP tool in backend/src/ai_chatbot/tools/add_tags_tool.py
- [ ] T060 [P] [US5] Create set_due_date MCP tool in backend/src/ai_chatbot/tools/set_due_date_tool.py
- [ ] T061 [P] [US5] Create set_recurring MCP tool in backend/src/ai_chatbot/tools/set_recurring_tool.py
- [ ] T062 [US5] Register new MCP tools in backend/src/ai_chatbot/tools/registration.py and loader.py
- [ ] T063 [US5] Update chat-interface.tsx to track session_id across messages in frontend/src/components/chat/chat-interface.tsx

**Checkpoint**: Chatbot maintains conversation context, resolves "it"/"that task", supports all new features via NL.

---

## Phase 8: User Story 6 – Cloud Kubernetes Deployment (Priority: P3)

**Goal**: Full system deployed to DOKS with Redpanda, Dapr, and all microservices

**Independent Test**: Deploy Helm charts to DOKS, verify all pods Running, test end-to-end flow

### Implementation for User Story 6

- [ ] T064 [US6] Create DOKS cluster using doctl (3x s-2vcpu-4gb nodes) – document in docs/doks-setup.md
- [ ] T065 [US6] Install Dapr on DOKS cluster via Helm (dapr/dapr chart to dapr-system namespace)
- [ ] T066 [US6] Install Redpanda on DOKS cluster via Helm (redpanda/redpanda chart, single node, 0.5 CPU / 1 GiB)
- [ ] T067 [P] [US6] Create Helm template for Dapr pub/sub component in helm/todo-app/templates/dapr-pubsub.yaml
- [ ] T068 [P] [US6] Create Helm template for Dapr state store component in helm/todo-app/templates/dapr-statestore.yaml
- [ ] T069 [P] [US6] Create Helm templates for Reminder Service (deployment + service) in helm/todo-app/templates/reminder-deployment.yaml and reminder-service.yaml
- [ ] T070 [P] [US6] Create Helm templates for Recurrence Service (deployment + service) in helm/todo-app/templates/recurrence-deployment.yaml and recurrence-service.yaml
- [ ] T071 [P] [US6] Create Helm templates for Audit Service (deployment + service) in helm/todo-app/templates/audit-deployment.yaml and audit-service.yaml
- [ ] T072 [US6] Add Dapr sidecar annotations to all Deployment templates (backend, reminder, recurrence, audit) in helm/todo-app/templates/
- [ ] T073 [US6] Update helm/todo-app/values.yaml with microservice configs, Dapr settings, and Redpanda connection
- [ ] T074 [US6] Create values-doks.yaml with DOKS-specific overrides (DOCR images, Neon DB URL, secrets) in helm/todo-app/values-doks.yaml
- [ ] T075 [US6] Build and push Docker images to DOCR for backend, frontend, and all 3 microservices
- [ ] T076 [US6] Deploy full stack to DOKS: helm install todo-app with values-doks.yaml
- [ ] T077 [US6] Configure HPA (Horizontal Pod Autoscaler) for backend and frontend in helm/todo-app/templates/hpa.yaml
- [ ] T078 [US6] Verify end-to-end: login, create task with priority/tags/due date, search, chatbot, reminders on DOKS

**Checkpoint**: Full system running on cloud Kubernetes with all features functional.

---

## Phase 9: User Story 7 – Audit Trail Service (Priority: P3)

**Goal**: Immutable audit log of all task operations, queryable by admin

**Independent Test**: Perform task operations, query audit API, verify entries

**Depends on**: US3 (needs events flowing)

### Implementation for User Story 7

- [ ] T079 [US7] Implement Audit Service event handler in services/audit/main.py (subscribe to tasks topic, write AuditEntry to PostgreSQL)
- [ ] T080 [US7] Add idempotency check (event_id unique constraint) to Audit Service in services/audit/main.py
- [ ] T081 [US7] Create admin audit log endpoint GET /api/admin/audit in backend/src/api/audit.py (filter by user_id, task_id, operation, date range)
- [ ] T082 [US7] Add admin JWT verification to audit endpoint in backend/src/api/audit.py

**Checkpoint**: Audit service captures 100% of task events. Admin can query by user/date/operation.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple stories

- [ ] T083 [P] Update backend/Dockerfile for new dependencies and Dapr compatibility
- [ ] T084 [P] Update docker-compose.yml to include Redpanda, Dapr, and microservices for local dev
- [ ] T085 [P] Update README.md with Phase V architecture, deployment instructions, and new features
- [ ] T086 Update HF Spaces deployment (todo-backend) with new models and dependencies
- [ ] T087 Update Vercel frontend deployment with new UI components
- [ ] T088 End-to-end smoke test: full user journey across all features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 – BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 – MVP, start first
- **US2 (Phase 4)**: Depends on Phase 2 – can parallel with US1
- **US3 (Phase 5)**: Depends on US1 + US2 (needs all task fields for events)
- **US4 (Phase 6)**: Depends on US3 (needs task.completed events)
- **US5 (Phase 7)**: Depends on US1 (needs priority/tag features for new MCP tools)
- **US6 (Phase 8)**: Depends on US3, US4, US7 (needs all services for deployment)
- **US7 (Phase 9)**: Depends on US3 (needs events flowing)
- **Polish (Phase 10)**: Depends on all desired stories complete

### Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Foundation)
                        ↓
              ┌─────────┼─────────┐
              ↓         ↓         ↓
          US1 (P1)  US2 (P1)  US5 (P2)*
              │         │         │
              └────┬────┘         │
                   ↓              │
               US3 (P2)          │
              ┌────┼────┐        │
              ↓         ↓        │
          US4 (P2)  US7 (P3)    │
              │         │        │
              └────┬────┘────────┘
                   ↓
               US6 (P3) → Polish

* US5 can start after US1 but benefits from US2 fields too
```

### Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005, T006, T007 all parallel
- **Phase 2**: T009, T010, T011 parallel (independent models)
- **Phase 3+**: US1 and US2 can run in parallel after Phase 2
- **Phase 7**: T057–T061 (5 new MCP tools) all parallel
- **Phase 8**: T067–T071 (Helm templates) all parallel

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundation
3. Complete Phase 3: US1 (Priorities, Tags, Search)
4. **STOP and VALIDATE**: Test sorting, filtering, search independently
5. Deploy to HF/Vercel for demo

### Incremental Delivery

1. Setup + Foundation → Ready
2. US1 (Priorities/Tags) → MVP Demo
3. US2 (Due Dates/Reminders) → Productivity features
4. US3 (Event-Driven) → Kafka/Dapr backbone
5. US4 (Recurring) + US7 (Audit) → Event consumers
6. US5 (Chatbot History) → AI enhancement
7. US6 (Cloud Deploy) → DOKS deployment
8. Polish → Final integration

---

## Notes

- Total: **88 tasks** across 10 phases
- US1: 10 tasks | US2: 10 tasks | US3: 7 tasks | US4: 8 tasks | US5: 12 tasks | US6: 15 tasks | US7: 4 tasks
- Setup: 7 tasks | Foundation: 9 tasks | Polish: 6 tasks
- No test tasks included (not requested in spec)
- Each user story checkpoint enables independent demo/validation
