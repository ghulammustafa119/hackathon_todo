# Implementation Plan: Phase I - In-Memory Console Todo App

**Branch**: `001-phase1-console-app` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase1-console-app/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase I implements a fully functional in-memory console-based Todo application with core CRUD operations (Create, Read, Update, Delete, Mark Complete) and menu-driven user interface. Technical approach uses Python with standard library data structures (dict, list) for in-memory storage. No external dependencies, databases, or persistence required by Phase I specification.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: None (standard library only)
**Storage**: In-memory (Python dict/list structures, no persistence)
**Testing**: pytest (optional for Phase I)
**Target Platform**: Linux/macOS/Windows console (Python 3.11+)
**Project Type**: single
**Performance Goals**: Task operations complete in <100ms for <1000 tasks in memory
**Constraints**: No external services, no databases, no persistence, single-threaded only, no async
**Scale/Scope**: Single-user console app, in-memory storage, no size limits specified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Spec-Driven Development (Mandatory)**: ✅ PASS
- Feature originates from written specification at `/specs/001-phase1-console-app/spec.md`
- Acceptance criteria defined (SC-001 through SC-006)
- Clear behavior definitions in user stories (Given-When-Then scenarios)
- **Action**: Use Claude Code for implementation (manual coding prohibited)

**Constitution-First Governance**: ✅ PASS
- All implementation decisions comply with `.specify/memory/constitution.md`
- Ambiguities resolved at spec level (no [NEEDS CLARIFICATION] markers remain)
- Specification status: Final (ready for implementation)

**Phase I Scope Compliance**: ✅ PASS
- ✅ Includes: In-memory task management, console-based user interaction, core CRUD functionality
- ✅ Excludes: Databases, file persistence, authentication, web interfaces, APIs, AI/MCP/LLM integrations, background jobs/schedulers
- **Action**: Strict scope enforcement - no Phase II+ features

**Basic Level Feature Governance**: ✅ PASS
- ✅ Add Task (FR-001 to FR-003)
- ✅ Delete Task (FR-008, FR-009)
- ✅ Update Task (FR-006, FR-007)
- ✅ View Task List (FR-004, FR-005)
- ✅ Mark Task as Complete (FR-010)
- **Action**: All mandatory Phase I features present in specification

**GATE RESULT**: ✅ ALL GATES PASSED - Proceed to Phase 1 Design

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-console-app/
├── spec.md              # Feature specification (/sp.specify command output)
├── plan.md              # This file (/sp.plan command output)
├── data-model.md        # Phase 1 output (/sp.plan command - below)
├── quickstart.md        # Phase 1 output (/sp.plan command - below)
├── contracts/           # Phase 1 output - internal API contracts (below)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Option 1: Single project (SELECTED - Phase I console app)
todo_console/
├── main.py             # Application entry point
├── models/
│   └── task.py          # Task data model
├── services/
│   ├── storage.py       # In-memory task storage
│   └── operations.py    # Task CRUD operations
└── cli/
    ├── menu.py          # Menu display and navigation
    ├── input.py         # User input collection
    └── render.py        # Console output rendering

tests/
├── unit/
│   ├── test_storage.py
│   ├── test_operations.py
│   └── test_cli.py
└── integration/
    └── test_full_workflow.py
```

**Structure Decision**: Selected Option 1 (Single project) for Phase I in-memory console application. This aligns with Phase I scope (no frontend/backend separation, no web interface needed). All modules contained in `todo_console/` package for clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations found. All gates passed without complexity violations.

---

## Phase 0: Outline & Research

### Extract Unknowns from Technical Context

No unknowns identified - all technical decisions are clear:
- Python version: 3.11 (standard choice, no special requirements)
- Dependencies: None (standard library sufficient)
- Storage: In-memory dict/list (clear requirement from spec)
- Testing: pytest (standard Python testing)

### Consolidate Findings

**Decision**: No external research required for Phase I
**Rationale**: All technical requirements are specified and standard library sufficient. Phase I explicitly excludes external services, databases, APIs, and complex integrations that would require research.
**Alternatives Considered**: N/A - no alternatives to evaluate

**Output**: No `research.md` needed - Phase 0 skipped (all unknowns resolved by specification)

---

## Phase 1: Design & Contracts

**Prerequisites:** No Phase 0 output needed (all unknowns resolved)

### 1. Extract Entities from Feature Spec → `data-model.md`

**Task Entity**
- Name: Task
- Fields:
  - id: unique integer (auto-incrementing)
  - title: non-empty string (required)
  - description: optional string
  - completed: boolean (default: false)
- Relationships: None (single entity for Phase I)
- Validation Rules:
  - title cannot be empty or whitespace only
  - id must be unique and positive integer
  - completed is boolean, defaulting to false on creation
- State Transitions:
  - completed: false → true (Mark Complete operation)
  - completed: true → false (Mark Complete operation - toggle behavior)
  - title/description: always mutable (Update operation)

### 2. Generate API Contracts from Functional Requirements

Since Phase I is console-only (no REST/GraphQL API), "contracts" are internal service boundaries:

**Storage Service Contract**
```python
class TaskStorage:
    def create(self, title: str, description: str = None) -> int:  # Returns task_id
    def get(self, task_id: int) -> Optional[Task]
    def get_all(self) -> List[Task]
    def update(self, task_id: int, **kwargs) -> bool
    def delete(self, task_id: int) -> bool
    def exists(self, task_id: int) -> bool
```

**Operations Service Contract**
```python
class TaskOperations:
    def create_task(self, title: str, description: str = None) -> dict:  # Returns task with id
    def update_task(self, task_id: int, title: str = None, description: str = None) -> dict
    def delete_task(self, task_id: int) -> dict:
    def toggle_completion(self, task_id: int) -> dict:
    def list_tasks(self) -> List[dict]:
```

**Input Validation Contract**
```python
class InputValidator:
    def validate_task_id(self, task_id: str) -> Optional[int]:  # Returns int or None
    def validate_title(self, title: str) -> bool:
    def validate_menu_choice(self, choice: str, valid_range: Tuple[int, int]) -> bool:
```

**Output Format Contract**
```python
class ConsoleRenderer:
    def display_menu(self, title: str, options: List[str]) -> None:
    def display_task_list(self, tasks: List[Task]) -> None:
    def display_success(self, message: str) -> None:
    def display_error(self, message: str) -> None:
    def display_prompt(self, prompt: str) -> None:
```

**Output**: Contract definitions created in `contracts/` directory (internal Python contracts, not OpenAPI/GraphQL schemas - Phase I is console-only)

### 3. Agent Context Update

Running `.specify/scripts/bash/update-agent-context.sh` to update agent context with Phase I technology choices.

**Agent-Specific Updates**:
- **Architecture**: In-memory console application (single project structure)
- **Language**: Python 3.11 with standard library only
- **Storage**: In-memory (no persistence, no database)
- **Constraints**: Single-threaded, no async, no external dependencies

**Action**: Context update preserves existing skills and adds Phase I context for task generation.

### 4. Re-evaluate Constitution Check Post-Design

**Constitution Check**: ✅ PASSED (re-verified after design)
- ✅ Design aligns with Phase I scope (in-memory, console, no persistence)
- ✅ No Phase II+ features introduced
- ✅ Data model uses primitive Python types (dict, list, bool, int, str)
- ✅ Service contracts maintain separation of concerns
- ✅ Implementation will use Claude Code only (no manual coding)

**GATE RESULT**: ✅ READY FOR TASK GENERATION - proceed to `/sp.tasks`

---

## Summary of Design Artifacts Generated

1. **data-model.md**: Task entity with fields, validation rules, state transitions
2. **contracts/**: Internal Python service contracts for storage, operations, validation, rendering
3. **agent context updated**: Phase I technology stack and constraints documented
4. **quickstart.md**: Developer quickstart guide for implementation (next section)

## Next Steps

Run `/sp.tasks` to generate implementation tasks based on:
- User stories from spec.md (P1: Add Task, List Tasks, Mark Complete; P2: Update Task, Delete Task)
- Data model from data-model.md (Task entity)
- Service contracts from contracts/ directory
- Project structure defined above

This will produce `tasks.md` with task breakdown organized by user story for Claude Code implementation.
