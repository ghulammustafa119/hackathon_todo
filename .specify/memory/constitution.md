<!--
SYNC IMPACT REPORT
==================
Version Change: Initial → 1.0.0
Rationale: Initial constitution adoption for Todo Evolution Project

Modified Principles: N/A (initial constitution)

Added Sections:
  - Core Development Principles (Spec-Driven Development, Constitution-First)
  - Phase Governance Model (5-phase evolution)
  - Specification Requirements (required artifacts per phase)
  - Todo Feature Governance (Basic, Intermediate, Advanced levels)
  - AI Chatbot & Agent Governance (Agent Architecture, MCP Tools, NL Authority)
  - Authentication & Security Governance
  - Stateless System Rule
  - Cloud-Native & Deployment Governance (Phase IV & V)
  - Event-Driven Architecture Rules
  - Reusable Intelligence & Bonus Scope
  - Evaluation Alignment
  - Final Authority

Removed Sections: N/A (initial constitution)

Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section aligns with phase governance
  ✅ spec-template.md - User story priorities (P1/P2/P3) align with feature governance
  ✅ tasks-template.md - Task organization by user story aligns with priorities

Follow-up TODOs: None - all placeholders filled
-->

# Todo Evolution Project – Spec Constitution

## Core Principles

### I. Spec-Driven Development (Mandatory)

All functionality MUST originate from Markdown specifications. No feature may be implemented without:
- A written Spec
- Acceptance criteria
- Clear behavior definitions

Claude Code MUST be used to generate all implementation. Manual code writing is strictly prohibited.

> The engineer's role is to refine specifications until correct code is generated.

**Rationale**: Specifications serve as the single source of truth, ensuring architectural thinking takes precedence over manual coding and enabling AI agents to function as implementation engines.

---

### II. Constitution-First Governance

This Constitution overrides all implementation decisions. All Specs must comply with this Constitution. Any ambiguity must be resolved at the **spec level**, never in code.

**Rationale**: Establishes clear governance hierarchy where Constitution > Spec > Implementation, preventing ad-hoc decisions and ensuring alignment with project principles.

---

## Phase Governance Model

This Constitution applies **uniformly across all five phases**.

| Phase | Focus | Governance Scope |
|-------|-------|------------------|
| Phase I | In-memory console app | Core CRUD + SDD |
| Phase II | Full-stack web app | Auth, DB, REST |
| Phase III | AI Chatbot | Agents + MCP |
| Phase IV | Local Kubernetes | Containers + Helm |
| Phase V | Cloud & Event-Driven | Kafka + Dapr |

**Rationale**: Ensures consistent governance principles apply throughout the entire evolution from simple console app to cloud-native system.

---

## Specification Requirements

### Required Spec Artifacts (Per Phase)

Each phase MUST include:
- Feature specs (`/specs/features/`)
- API specs (`/specs/api/`)
- Database specs (`/specs/database/`)
- UI specs where applicable (`/specs/ui/`)
- Architecture updates if scope changes

All specs MUST be written in Markdown and referenced explicitly when invoking Claude Code.

### Spec Refinement Rule

If generated code is incorrect:
- ❌ Do NOT edit code manually
- ✅ Update the spec
- ✅ Re-run Claude Code

**Rationale**: Treats code correctness failures as specification problems, not implementation issues, maintaining spec-as-truth methodology.

---

## Todo Feature Governance

### Basic Level (All Phases)

The following features are mandatory foundations:
- Add Task
- Delete Task
- Update Task
- View Task List
- Mark Task as Complete

These must exist in:
- Phase I (Console)
- Phase II (Web)
- Phase III (Chatbot via MCP tools)

### Intermediate Level (Phase V)

- Priorities & Tags
- Search & Filter
- Sorting

These features must be:
- Specified
- Persisted
- Queryable
- Accessible via AI chatbot

### Advanced Level (Phase V)

- Recurring Tasks
- Due Dates & Reminders
- Event-driven processing using Kafka
- Decoupled services for reminders and recurrence

**Rationale**: Progressive feature complexity aligned with evolution phases, ensuring foundational features are present in all phases while advanced features are introduced in cloud-native environment.

---

## AI Chatbot & Agent Governance (Phase III+)

### Agent Architecture

AI logic MUST use **OpenAI Agents SDK**. Tool execution MUST use **Official MCP SDK**. Agents MUST be stateless. All state MUST be persisted in database.

### MCP Tool Rules

Each task operation MUST be exposed as an MCP tool. Tools MUST:
- Be stateless
- Validate ownership via user_id
- Persist changes to database

Agents MAY chain tools in a single turn.

### Natural Language Authority

Natural language is a **first-class interface**. Users must be able to manage tasks conversationally. The agent decides tool usage based on intent, not keywords alone.

**Rationale**: Enables conversational AI interaction while maintaining stateless architecture and proper data persistence boundaries.

---

## Authentication & Security Governance

Authentication is mandatory from Phase II onward. Better Auth MUST issue JWT tokens. Backend MUST verify JWTs independently. All data access MUST be scoped to authenticated user. Requests without valid JWT MUST return `401 Unauthorized`.

**Rationale**: Ensures secure multi-user system with proper authentication and authorization boundaries.

---

## Stateless System Rule

From Phase III onward:
- No server memory state is allowed
- Conversation context MUST be stored in database
- System must survive restarts without data loss
- Any instance must handle any request

**Rationale**: Enables horizontal scaling, resilience, and proper cloud-native architecture where state is externalized.

---

## Cloud-Native & Deployment Governance

### Phase IV – Local Kubernetes

Frontend and backend MUST be containerized. Deployment MUST use:
- Minikube
- Helm charts

AI-assisted DevOps tools (kubectl-ai, kagent) are encouraged.

### Phase V – Cloud Deployment

Deployment MUST target:
- DigitalOcean Kubernetes (DOKS), or
- GKE / AKS

Dapr MUST be used for:
- Pub/Sub
- State
- Bindings
- Service invocation

Kafka MUST be used for event-driven workflows.

**Rationale**: Establishes containerization, orchestration, and cloud-native infrastructure requirements for scalable deployment.

---

## Event-Driven Architecture Rules (Phase V)

Task operations MUST emit Kafka events. Services MUST communicate via events, not direct calls. Reminder, recurrence, and audit logic MUST be decoupled. Event schemas MUST be versioned and documented.

**Rationale**: Enables loose coupling, scalability, and independent evolution of services through event-driven communication patterns.

---

## Reusable Intelligence & Bonus Scope

If implemented:
- Agent Skills
- Sub-agents
- Cloud-Native Blueprints
- Multi-language support (Urdu)
- Voice commands

These MUST also be spec-driven and governed by this Constitution.

**Rationale**: Ensures even optional/innovative features follow the same rigorous spec-driven development principles.

---

## Evaluation Alignment

This project is evaluated on:
- Spec clarity
- Architectural correctness
- Proper use of Claude Code
- Stateless & cloud-native design
- Correct application of Agents, MCP, Kafka, and Dapr

Manual shortcuts reduce score.

---

## Governance

This Constitution exists to ensure that the Todo project is not merely functional, but a **reference-grade example of Spec-Driven, AI-Native, Cloud-Ready software architecture**.

### Amendment Process

- Amendments require documentation, rationale, and explicit version increment
- All contributors and AI agents are bound by this Constitution
- Templates (plan, spec, tasks) must align with Constitution updates
- When Constitution changes, all dependent templates must be reviewed and updated

### Versioning Policy

- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review

- All PRs/reviews must verify compliance with Constitution principles
- Complexity must be justified against Constitution constraints
- Constitution overrides all other practices and guidance

### Final Authority

If a conflict exists between:
- Code and Spec → Spec wins
- Spec and Constitution → Constitution wins
- Assumption and Documentation → Documentation wins

---

**Version**: 1.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02
