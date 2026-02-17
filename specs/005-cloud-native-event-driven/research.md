# Research: Phase V – Cloud-Native Event-Driven Architecture

**Date**: 2026-02-17 | **Branch**: `005-cloud-native-event-driven`

## 1. Event Streaming Platform

### Decision: Redpanda (self-hosted, single node)

**Rationale**: Kafka-compatible API with ~1/3 the resource footprint. Single binary (no ZooKeeper/KRaft controller). Ideal for a learning/hackathon project on resource-constrained DOKS.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Strimzi (Apache Kafka on K8s) | True Kafka, production-grade | Heavy (1-2 GiB per broker + ZooKeeper/KRaft), slow startup | Rejected: too heavy for 3-node DOKS |
| Confluent Cloud | Fully managed, zero ops | $50-100+/month, external dependency | Rejected: cost |
| Redpanda Cloud | Managed Redpanda | Adds cost, vendor lock-in | Rejected: self-hosted is free |
| **Redpanda self-hosted** | Lightweight (~512 MiB), Kafka-compatible, single binary | Single node = no replication | **Chosen** |

**Deployment**: Redpanda Helm chart, single node, 0.5 CPU / 1 GiB RAM, 10 GiB persistent volume.

---

## 2. Dapr Integration

### Decision: Dapr sidecar model with pub/sub (Kafka), state store (PostgreSQL), and service invocation

**Rationale**: Constitution mandates Dapr for pub/sub, state, bindings, and service invocation. Dapr abstracts infrastructure behind standard HTTP APIs.

**Key Components**:

| Component | Type | Backing Service | Used By |
|-----------|------|-----------------|---------|
| `taskevents` | `pubsub.kafka` | Redpanda | Backend (publish), all microservices (subscribe) |
| `statestore` | `state.postgresql` | Neon PostgreSQL | Reminder service, Recurrence service |
| `todo-secrets` | `secretstores.kubernetes` | K8s Secrets | All services |

**Dapr System Overhead**: ~512 MiB RAM for 4 system pods (operator, injector, placement, sentry). ~64-256 MiB per sidecar.

---

## 3. Microservice Architecture

### Decision: 3 event-driven microservices (Reminder, Recurrence, Audit)

**Event Schema**: CloudEvents v1.0 format with `task.created`, `task.updated`, `task.deleted`, `task.completed` event types. Single `tasks` topic with event_type routing.

**Reminder Service**:
- Consumes task events, schedules reminders using Dapr state store
- Background scheduler checks every 30s for due reminders
- Publishes `reminder.fired` to `notifications` topic

**Recurrence Service**:
- Consumes `task.completed` events
- Publishes `task.create.requested` command event (backend creates the task)
- Uses `croniter` library for cron parsing

**Audit Service**:
- Consumes ALL task events
- Writes to PostgreSQL `audit_entries` table (direct SQLModel, needs SQL queries)
- Idempotent via unique `event_id` constraint

**Reliability**: Direct publish with retry. Outbox pattern documented as enhancement path.

---

## 4. Conversation History

### Decision: Extend existing PostgreSQL models with session timeout and task references

**Rationale**: ConversationMessage and ConversationHistory models already exist. Extend with session semantics (30-min timeout), task_references (JSON), and token_count for context management.

**Context Strategy**: Sliding window (last 20 messages, 4000 token budget). Inject referenced task state as system message for pronoun resolution.

**Alternatives Considered**:

| Option | Verdict |
|--------|---------|
| Redis session cache | Rejected: extra infrastructure, PostgreSQL sufficient at this scale |
| Separate conversation DB | Rejected: operational complexity |
| Vector store for history | Rejected: overkill for 30-min sessions |

---

## 5. Cloud Platform (DOKS)

### Decision: DigitalOcean Kubernetes, 3x s-2vcpu-4gb nodes (~$72/mo)

**Total Monthly Cost Estimate**:

| Service | Cost |
|---------|------|
| DOKS Cluster (3 nodes) | $72 |
| DO Load Balancer | $12 |
| DO Block Storage (10 GiB) | $1 |
| DO Container Registry | $5 |
| Neon PostgreSQL (free tier) | $0 |
| **Total** | **~$90/mo** |

**Database**: Continue with Neon PostgreSQL (already working, free tier).

**Container Registry**: DigitalOcean Container Registry (DOCR), native DOKS integration.

**Ingress**: DO NGINX Ingress Controller (auto-provisions Load Balancer).

---

## 6. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Redpanda-Dapr compatibility | Fallback to Strimzi KRaft single-broker |
| Neon cold starts | Keep-alive cron or upgrade to Pro ($19/mo) |
| DOKS resources too tight | Monitor; upgrade to s-4vcpu-8gb if needed |
| Dapr sidecar overhead | Reduce limits; consider Dapr shared mode |
