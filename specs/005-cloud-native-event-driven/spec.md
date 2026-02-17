# Feature Specification: Phase V – Cloud-Native with Event-Driven Architecture

**Feature Branch**: `005-cloud-native-event-driven`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "Phase V - Cloud-Native with Event-Driven Architecture: Deploy to cloud Kubernetes (DOKS/GKE/AKS), integrate Kafka for event streaming, add Dapr for pub/sub and state management, implement advanced todo features (priorities, tags, search, filtering, sorting, due dates, recurring tasks, reminders), build decoupled microservices (reminder service, recurrence service, audit service), and enhance AI chatbot with conversation history and multi-turn support."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Priorities, Tags, and Organization (Priority: P1)

As a user, I want to assign priorities (High, Medium, Low) and tags (custom labels) to my tasks, so I can organize and find tasks quickly. I can sort my task list by priority, due date, or creation date, and filter tasks by tag, priority, or completion status. I can also search tasks by keyword across title and description.

**Why this priority**: Organization features (priorities, tags, search, filtering, sorting) are the foundation that all other Phase V features build upon. Without structured task data, event-driven features and AI enhancements have no meaningful data to operate on.

**Independent Test**: Can be fully tested by creating tasks with various priorities and tags, then verifying sort, filter, and search produce correct results. Delivers immediate organizational value to users.

**Acceptance Scenarios**:

1. **Given** a logged-in user creating a task, **When** they set priority to "High" and add tags "work" and "urgent", **Then** the task is saved with those attributes and displayed with priority badge and tag chips.
2. **Given** a user with 10+ tasks of varying priorities, **When** they sort by priority descending, **Then** High-priority tasks appear first, then Medium, then Low.
3. **Given** a user with tagged tasks, **When** they filter by tag "work", **Then** only tasks tagged "work" are displayed.
4. **Given** a user searching for "meeting", **When** they enter the search term, **Then** all tasks with "meeting" in the title or description are returned.
5. **Given** a user with tasks, **When** they filter by "completed" status, **Then** only completed tasks are shown.

---

### User Story 2 - Due Dates and Reminders (Priority: P1)

As a user, I want to set due dates on tasks and receive reminders before a task is due, so I never miss a deadline. Reminders are sent at a configurable time before the due date (default: 1 hour before). Overdue tasks are visually highlighted.

**Why this priority**: Due dates and reminders are core productivity features that drive the need for event-driven architecture (reminder service). They provide the primary use case for Kafka events and Dapr integration.

**Independent Test**: Can be tested by creating a task with a due date, verifying it appears on the dashboard with due date display, and confirming the reminder service triggers a notification at the correct time.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they create a task with a due date of tomorrow at 3:00 PM, **Then** the task displays the due date and a countdown indicator.
2. **Given** a task with a due date 1 hour from now, **When** the reminder time arrives, **Then** the user sees a reminder notification in the app.
3. **Given** a task whose due date has passed, **When** the user views the task list, **Then** the overdue task is visually highlighted (e.g., red border or badge).
4. **Given** a user editing a task, **When** they change the reminder lead time to 30 minutes, **Then** the reminder is rescheduled accordingly.

---

### User Story 3 - Event-Driven Task Operations (Priority: P2)

As a system operator, I want all task operations (create, update, delete, complete) to emit events, so that downstream services (reminders, recurrence, audit) can react independently without direct coupling. Each event contains the full task state and metadata.

**Why this priority**: The event-driven backbone is required by the Constitution and enables the decoupled microservice architecture. It must be in place before reminder, recurrence, and audit services can function.

**Independent Test**: Can be tested by performing task operations and verifying events are published to the event stream with correct schema and content. Downstream consumers can be verified independently.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the task is saved, **Then** a "task.created" event is published containing task ID, user ID, title, priority, tags, due date, and timestamp.
2. **Given** a user completes a task, **When** the completion is saved, **Then** a "task.completed" event is published and the audit service records it.
3. **Given** a user updates a task's due date, **When** the update is saved, **Then** a "task.updated" event is published and the reminder service reschedules accordingly.
4. **Given** an event consumer is temporarily unavailable, **When** events are published, **Then** events are retained and delivered when the consumer recovers (at-least-once delivery).

---

### User Story 4 - Recurring Tasks (Priority: P2)

As a user, I want to create recurring tasks that automatically regenerate on a schedule (daily, weekly, monthly, or custom cron), so I don't have to manually recreate routine tasks.

**Why this priority**: Recurring tasks demonstrate the power of event-driven architecture with a dedicated recurrence service that listens for completion events and creates new task instances.

**Independent Test**: Can be tested by creating a recurring daily task, completing it, and verifying a new instance is automatically created for the next occurrence.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** they set recurrence to "daily", **Then** the task is marked as recurring with the specified schedule.
2. **Given** a recurring daily task is completed, **When** the completion event is processed, **Then** a new task instance is created with the next day's due date and the same title, priority, and tags.
3. **Given** a user with a weekly recurring task, **When** they edit the recurrence to "monthly", **Then** the next occurrence is rescheduled to one month from now.
4. **Given** a user deletes a recurring task, **When** they confirm deletion, **Then** the recurrence schedule is cancelled and no future instances are created.

---

### User Story 5 - AI Chatbot with Conversation History (Priority: P2)

As a user, I want the AI chatbot to remember our conversation history within a session, so I can have multi-turn conversations like "add a task called meeting" followed by "set it to high priority" without repeating context.

**Why this priority**: Conversation history fulfills the Phase V constitution requirement for stateful intelligence (deferred from Phase III). It enhances the chatbot from a single-command tool to a conversational assistant.

**Independent Test**: Can be tested by sending a sequence of related messages to the chatbot and verifying it maintains context across turns, correctly referencing previous tasks and operations.

**Acceptance Scenarios**:

1. **Given** a user says "add a task called grocery shopping", **When** the chatbot creates the task, **Then** the conversation is stored in the database with the task reference.
2. **Given** the previous message created a task, **When** the user says "set it to high priority", **Then** the chatbot understands "it" refers to the grocery shopping task and updates its priority.
3. **Given** a user has an ongoing conversation, **When** they say "show my tasks tagged work", **Then** the chatbot uses the new filtering capabilities to return only work-tagged tasks.
4. **Given** a user returns after a session timeout, **When** they start a new conversation, **Then** the chatbot starts fresh but previous history is retained in the database for auditing.

---

### User Story 6 - Cloud Kubernetes Deployment (Priority: P3)

As a system operator, I want the entire application (frontend, backend, event infrastructure, microservices) deployed to a managed cloud Kubernetes cluster, so the system runs in a production-grade environment with auto-scaling and high availability.

**Why this priority**: Cloud deployment is the culmination of Phase V but depends on all other features being functional first. It packages everything into a production-ready deployment.

**Independent Test**: Can be tested by deploying the Helm charts to a cloud Kubernetes cluster and verifying all services start, health checks pass, and end-to-end user flows work.

**Acceptance Scenarios**:

1. **Given** a configured cloud Kubernetes cluster, **When** the Helm charts are deployed, **Then** all pods (frontend, backend, Kafka, Dapr sidecars, microservices) reach Running state within 5 minutes.
2. **Given** a deployed system, **When** a user accesses the frontend URL, **Then** they can log in, manage tasks, and use the AI chatbot.
3. **Given** a running deployment, **When** one backend pod is terminated, **Then** Kubernetes restarts it and service is restored within 60 seconds.
4. **Given** increased load, **When** CPU exceeds 70% threshold, **Then** horizontal pod autoscaler adds additional replicas.

---

### User Story 7 - Audit Trail Service (Priority: P3)

As a system administrator, I want an audit trail of all task operations, so I can review user activity for compliance, debugging, and analytics purposes. The audit service consumes task events and stores an immutable log.

**Why this priority**: Audit is a downstream consumer that depends on the event backbone (Story 3) being in place. It adds observability but is not required for core user functionality.

**Independent Test**: Can be tested by performing task operations and verifying the audit service records each event with timestamp, user ID, operation type, and before/after task state.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the "task.created" event is consumed by the audit service, **Then** an audit entry is recorded with user ID, operation "CREATE", task data, and timestamp.
2. **Given** a user updates a task, **When** the "task.updated" event is consumed, **Then** the audit entry includes both the previous and new task state.
3. **Given** an administrator queries the audit log, **When** they filter by user ID and date range, **Then** they see all task operations for that user in chronological order.

---

### Edge Cases

- What happens when a recurring task's due date falls on a weekend or holiday? The system creates the task as-is; users can manually adjust.
- What happens when a user deletes a task that has pending reminders? The reminder service cancels all scheduled reminders for that task upon receiving the "task.deleted" event.
- What happens when Kafka is temporarily unavailable? Task operations succeed locally (database write), and events are published when Kafka recovers via an outbox pattern or retry mechanism.
- What happens when a user sets a due date in the past? The system accepts it but immediately marks the task as overdue.
- What happens when a search query returns no results? The system displays a "No tasks found" message with a suggestion to clear filters.
- What happens when the AI chatbot cannot resolve a pronoun reference (e.g., "set it to high")? The chatbot asks for clarification: "Which task would you like to update?"

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to assign a priority level (High, Medium, Low) to each task.
- **FR-002**: System MUST allow users to add one or more custom text tags to each task.
- **FR-003**: System MUST support sorting tasks by priority, due date, creation date, or title.
- **FR-004**: System MUST support filtering tasks by priority level, tag, completion status, and due date range.
- **FR-005**: System MUST support full-text search across task titles and descriptions.
- **FR-006**: System MUST allow users to set a due date and time on any task.
- **FR-007**: System MUST send in-app reminder notifications at a configurable lead time before a task's due date (default: 1 hour).
- **FR-008**: System MUST visually distinguish overdue tasks from on-time tasks.
- **FR-009**: System MUST publish an event for every task operation (create, update, delete, complete) containing full task state and metadata.
- **FR-010**: System MUST support event schema versioning so consumers can handle schema evolution.
- **FR-011**: System MUST allow users to configure recurring task schedules (daily, weekly, monthly, custom).
- **FR-012**: System MUST automatically create new task instances when a recurring task is completed, with the next scheduled due date.
- **FR-013**: System MUST store conversation history in the database, scoped per user and per session.
- **FR-014**: AI chatbot MUST resolve contextual references (e.g., "it", "that task", "the last one") using conversation history.
- **FR-015**: AI chatbot MUST support the new features via natural language (priorities, tags, search, filter, sort, due dates, recurring).
- **FR-016**: System MUST maintain an immutable audit log of all task operations with user ID, operation type, timestamp, and task state.
- **FR-017**: System MUST deploy to a managed cloud Kubernetes cluster with health checks, auto-restart, and horizontal pod autoscaling.
- **FR-018**: All inter-service communication MUST use event-driven messaging, not direct service-to-service calls (except API gateway to backend).
- **FR-019**: System MUST use Dapr for pub/sub messaging, state management, and service invocation.
- **FR-020**: System MUST guarantee at-least-once event delivery; consumers must handle duplicate events idempotently.

### Key Entities

- **Task** (extended): Existing task entity extended with priority (enum: High/Medium/Low), tags (list of strings), due_date (datetime, optional), reminder_lead_time (duration, default 1 hour), recurrence_rule (string, optional: daily/weekly/monthly/cron), recurrence_parent_id (reference to original recurring task).
- **TaskEvent**: Represents a published event with event_id, event_type (created/updated/deleted/completed), task_id, user_id, payload (full task state), schema_version, timestamp.
- **ConversationMessage**: A single message in a conversation with message_id, session_id, user_id, role (user/assistant), content, task_references (list of task IDs mentioned), timestamp.
- **ConversationSession**: Groups messages into sessions with session_id, user_id, started_at, last_active_at, is_active.
- **AuditEntry**: Immutable log entry with audit_id, user_id, operation_type, task_id, previous_state, new_state, timestamp.
- **ReminderSchedule**: Tracks scheduled reminders with reminder_id, task_id, user_id, remind_at (datetime), status (pending/sent/cancelled).

### Assumptions

- The project will use DigitalOcean Kubernetes (DOKS) as the primary cloud target, with Helm charts portable to GKE/AKS.
- Kafka will be deployed as a managed service or self-hosted within the cluster using Strimzi operator.
- Dapr will be deployed as sidecar containers alongside each microservice.
- Reminder notifications are in-app only (no email/SMS/push in Phase V scope).
- Conversation sessions expire after 30 minutes of inactivity; a new session is created on the next message.
- Event schema versioning uses integer versions (v1, v2, etc.) with backward compatibility.
- The audit log is append-only and queryable by administrators; no user-facing audit UI is in scope.
- Recurring task cron expressions follow standard 5-field cron syntax.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create, prioritize, tag, and search tasks with results appearing in under 2 seconds.
- **SC-002**: Task events are published and consumed by downstream services within 5 seconds of a task operation.
- **SC-003**: Recurring tasks automatically regenerate within 10 seconds of the previous instance being completed.
- **SC-004**: Reminder notifications are delivered within 1 minute of the scheduled reminder time.
- **SC-005**: AI chatbot correctly resolves contextual references in multi-turn conversations at least 80% of the time.
- **SC-006**: All services recover from a single pod failure within 60 seconds without data loss.
- **SC-007**: System supports at least 100 concurrent users performing task operations without degradation.
- **SC-008**: Audit log captures 100% of task operations with correct before/after state.
- **SC-009**: Cloud deployment completes successfully from Helm charts within 10 minutes on a fresh cluster.
- **SC-010**: End-to-end user flow (login, create task with priority/tags/due date, search, chatbot interaction) works on cloud deployment.
