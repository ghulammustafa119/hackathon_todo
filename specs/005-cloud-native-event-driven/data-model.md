# Data Model: Phase V – Cloud-Native Event-Driven Architecture

**Date**: 2026-02-17 | **Branch**: `005-cloud-native-event-driven`

## Entity Relationship Overview

```
User (existing)
  ├── Task (extended)
  │     ├── TaskEvent (published on every operation)
  │     ├── ReminderSchedule (managed by reminder service)
  │     └── AuditEntry (immutable log)
  ├── ConversationSession (replaces ConversationHistory)
  │     └── ConversationMessage (extended with task refs)
  └── Tag (many-to-many with Task)
```

---

## Extended Entities

### Task (Extended from Phase II)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (str) | PK | Existing |
| user_id | str | FK → User, indexed | Existing |
| title | str | required, min 1 char | Existing |
| description | str | optional | Existing |
| completed | bool | default: false | Existing |
| completed_at | datetime | optional | Existing |
| created_at | datetime | auto | Existing |
| updated_at | datetime | auto | Existing |
| **priority** | enum(high,medium,low) | default: medium | **NEW** |
| **due_date** | datetime | optional | **NEW** |
| **reminder_lead_time** | int (minutes) | default: 60 | **NEW** |
| **recurrence_rule** | str | optional (daily/weekly/monthly/cron) | **NEW** |
| **recurrence_parent_id** | UUID (str) | optional, FK → Task | **NEW** |

### Tag

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | |
| name | str | max 50, indexed | Unique per user |
| user_id | str | FK → User, indexed | |

### TaskTag (Junction Table)

| Field | Type | Constraints |
|-------|------|-------------|
| task_id | UUID (str) | FK → Task, PK |
| tag_id | int | FK → Tag, PK |

### TaskEvent

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| event_id | UUID (str) | PK | CloudEvents id |
| event_type | str | enum(created/updated/deleted/completed) | |
| task_id | UUID (str) | indexed | |
| user_id | str | indexed | |
| payload | JSON | full task state | |
| previous_state | JSON | optional, for updates | |
| schema_version | int | default: 1 | |
| timestamp | datetime | auto | |

### ConversationSession (Replaces ConversationHistory)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (str) | PK | |
| user_id | str | FK → User, indexed | |
| title | str | max 255, auto-generated | |
| started_at | datetime | auto | |
| last_active_at | datetime | auto-updated | |
| is_active | bool | default: true | |
| message_count | int | default: 0 | |
| timeout_minutes | int | default: 30 | |

### ConversationMessage (Extended)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | int | PK, auto-increment | Existing |
| session_id | str | FK → ConversationSession, indexed | Renamed from conversation_id |
| user_id | str | FK → User, indexed | Existing |
| role | str | enum(user/assistant/system) | Extended |
| content | str | required | Existing |
| timestamp | datetime | auto | Existing |
| **task_references** | str (JSON) | optional, array of task IDs | **NEW** |
| **token_count** | int | optional | **NEW** |
| **tool_calls** | str (JSON) | optional, tool call summaries | **NEW** |

### AuditEntry

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (str) | PK | |
| user_id | str | indexed | |
| operation_type | str | enum(CREATE/UPDATE/DELETE/COMPLETE) | |
| task_id | str | indexed | |
| previous_state | JSON | optional | |
| new_state | JSON | required | |
| event_id | str | unique, idempotency key | |
| schema_version | int | required | |
| timestamp | datetime | indexed | |
| created_at | datetime | auto | |

### ReminderSchedule

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (str) | PK | |
| task_id | str | indexed, unique | One reminder per task |
| user_id | str | indexed | |
| remind_at | datetime | indexed | When to fire |
| status | str | enum(pending/sent/cancelled) | |
| created_at | datetime | auto | |

### OutboxEvent (Enhancement)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (str) | PK | |
| event_type | str | required | |
| topic | str | default: 'tasks' | |
| payload | JSON | required | |
| created_at | datetime | auto | |
| published_at | datetime | optional | null = unpublished |
| retry_count | int | default: 0 | |

---

## Database Indexes

```sql
-- Task extensions
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_due_date ON task(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_task_recurrence_parent ON task(recurrence_parent_id) WHERE recurrence_parent_id IS NOT NULL;

-- Full-text search
CREATE INDEX idx_task_title_search ON task USING gin(to_tsvector('english', title));
CREATE INDEX idx_task_desc_search ON task USING gin(to_tsvector('english', description)) WHERE description IS NOT NULL;

-- Tag lookups
CREATE INDEX idx_tag_user_name ON tag(user_id, name);
CREATE INDEX idx_tasktag_task ON tasktag(task_id);
CREATE INDEX idx_tasktag_tag ON tasktag(tag_id);

-- Audit
CREATE UNIQUE INDEX idx_audit_event_id ON audit_entries(event_id);
CREATE INDEX idx_audit_user_timestamp ON audit_entries(user_id, timestamp);

-- Reminder
CREATE INDEX idx_reminder_pending ON reminder_schedule(remind_at) WHERE status = 'pending';

-- Conversation
CREATE INDEX idx_session_user_active ON conversationsession(user_id, is_active, last_active_at);

-- Outbox
CREATE INDEX idx_outbox_unpublished ON outbox_events(created_at) WHERE published_at IS NULL;
```

---

## State Transitions

### Task Lifecycle
```
created → updated* → completed → (recurring: new instance created)
                   → deleted
```

### Reminder Lifecycle
```
pending → sent (on remind_at)
pending → cancelled (on task.deleted or task.updated with no due_date)
```

### Conversation Session Lifecycle
```
active → active (each message refreshes last_active_at)
active → expired (30 min inactivity, next message creates new session)
```
