# Tasks: Phase I - In-Memory Console Todo App

**Input**: Design documents from `/specs/001-phase1-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md (required for entity mapping), contracts/ (required for service boundaries)
**Tests**: Tests are OPTIONAL for Phase I - no tests explicitly requested in specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `todo_console/`, `src/` (not needed for Phase I), `tests/`
- Paths shown below use `todo_console/` package structure as defined in plan.md

<!--
  ============================================================================
  IMPORTANT: The tasks below are the ACTUAL IMPLEMENTATION TASKS.

  Each task is specific enough that Claude Code can complete it without
  additional context.

  Tasks are organized by user story (US1-US5) matching the spec.md
  priorities: P1 (Add, List, Complete) and P2 (Update, Delete).

  Each user story is an INDEPENDENTLY TESTABLE increment:
  - Can be developed independently
  - Can be tested independently
  - Delivers standalone value
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python package with __init__.py files
- [ ] T003 [P] Create models directory and module structure
- [ ] T004 [P] Create services directory and module structure
- [ ] T005 [P] Create cli directory and module structure
- [ ] T006 Create tests directory structure (unit and integration)

**Checkpoint**: Foundation structure ready - user story implementation can now begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T007 Implement Task dataclass in models/task.py
- [ ] T008 Implement TaskStorage in services/storage.py
- [ ] T009 Implement InputValidator in cli/input.py
- [ ] T010 Implement ConsoleRenderer in cli/render.py
- [ ] T011 Implement TaskOperations in services/operations.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks through console menu with required title and optional description

**Independent Test**: Can be fully tested by launching application, selecting "Add Task", entering title/description, and confirming task appears when listing tasks

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create main.py entry point in todo_console/
- [ ] T013 [P] [US1] Implement MainMenu in cli/menu.py for menu display and navigation
- [ ] T014 [US1] Wire TaskOperations.create_task() with InputValidator and TaskStorage in main application loop
- [ ] T015 [US1] Wire ConsoleRenderer.display_success() for task creation confirmation
- [ ] T016 [US1] Wire ConsoleRenderer.display_error() for title validation errors
- [ ] T017 [US1] Handle "Add Task" menu option (option 1) in main application loop

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - List All Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can view all currently stored tasks in readable, formatted list showing ID, title, and completion status

**Independent Test**: Can be fully tested by creating multiple tasks, selecting "List Tasks", and verifying all tasks display with correct information

### Implementation for User Story 2

- [ ] T018 [US2] Wire TaskOperations.list_tasks() to retrieve all tasks
- [ ] T019 [US2] Wire ConsoleRenderer.display_task_list() to format and display tasks
- [ ] T020 [US2] Handle "List Tasks" menu option (option 4) in main application loop
- [ ] T021 [US2] Display empty list message when no tasks exist

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Existing Task (Priority: P2)

**Goal**: Users can modify title and description of an existing task by providing valid task ID

**Independent Test**: Can be fully tested by creating a task, selecting "Update Task", entering task ID and new title/description, and confirming changes appear in task list

### Implementation for User Story 3

- [ ] T022 [P] [US3] Implement task_id prompt collection in main application loop
- [ ] T023 [P] [US3] Implement title and description prompts in main application loop
- [ ] T024 [US3] Wire TaskOperations.update_task() with InputValidator and TaskStorage
- [ ] T025 [US3] Wire ConsoleRenderer.display_success() for update confirmation
- [ ] T026 [US3] Wire ConsoleRenderer.display_error() for validation errors
- [ ] T027 [US3] Handle "Update Task" menu option (option 2) in main application loop

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can permanently remove a task from memory by providing its valid task ID

**Independent Test**: Can be fully tested by creating tasks, selecting "Delete Task", entering a valid task ID, and confirming task no longer appears in list

### Implementation for User Story 4

- [ ] T028 [US4] Wire TaskOperations.delete_task() with InputValidator and TaskStorage
- [ ] T029 [US4] Wire ConsoleRenderer.display_success() for deletion confirmation
- [ ] T030 [US4] Wire ConsoleRenderer.display_error() for task not found errors
- [ ] T031 [US4] Handle "Delete Task" menu option (option 3) in main application loop

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Mark Task as Complete (Priority: P1) 🎯 MVP

**Goal**: Users can toggle completion status of an existing task between not completed and completed

**Independent Test**: Can be fully tested by creating a task, selecting "Mark Task as Complete", entering task ID, and verifying completion status changes

### Implementation for User Story 5

- [ ] T032 [US5] Wire TaskOperations.toggle_completion() with InputValidator and TaskStorage
- [ ] T033 [US5] Wire ConsoleRenderer.display_success() for completion toggle confirmation
- [ ] T034 [US5] Wire ConsoleRenderer.display_error() for validation errors
- [ ] T035 [US5] Handle "Mark Task as Complete" menu option (option 5) in main application loop

**Checkpoint**: At this point, User Stories 1, 2, 3, 4, AND 5 should all work independently

---

## Phase 8: Integration & Application Loop

**Purpose**: Wire all components together in main application loop with menu navigation

- [ ] T036 Implement main application loop with MainMenu.display() and choice handling
- [ ] T037 Wire all menu options (1-6) to correct operations and user stories
- [ ] T038 Implement Exit option (option 6) with clean program termination
- [ ] T039 Add error handling for invalid menu choices with re-prompt
- [ ] T040 Ensure menu re-displays after each operation (except Exit)

**Checkpoint**: All user stories integrated in cohesive application flow

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T041 [P] Add input collection helpers in main.py (prompts with context)
- [ ] T042 Code cleanup and refactoring (remove unused imports, consistent naming)
- [ ] T043 Performance optimization (test with large task lists if time permits)
- [ ] T044 [P] Additional unit tests (if testing requested) - Phase I does not require tests
- [ ] T045 Run quickstart.md validation from quickstart guide

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P1 → P2 → P2)
- **Integration (Phase 8)**: Depends on all user stories being complete
- **Polish (Final Phase)**: Depends on Integration phase completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with T012-T020 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - May integrate with T012-T020 but should be independently testable
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - May integrate with T012-T020 but should be independently testable

### Within Each User Story

### User Story 1 (Add Task)
- Tests (if included): N/A (Phase I does not require tests)
- Models before services: T007 → T008
- Services before endpoints: T008 → T011, T014, T016
- Core implementation before integration: T007-T017
- Story complete before moving to next priority: All tasks in US1 phase complete

### User Story 2 (List Tasks)
- Tests (if included): N/A (Phase I does not require tests)
- Services before endpoints: T008, T011 → T018, T019, T021
- Endpoints/integration: T018-T020
- Story complete before moving to next priority: All tasks in US2 phase complete

### User Story 3 (Update Task)
- Tests (if included): N/A (Phase I does not require tests)
- Services before endpoints: T008, T011, T009 → T022-T026
- Endpoints/integration: T022-T027
- Story complete before moving to next priority: All tasks in US3 phase complete

### User Story 4 (Delete Task)
- Tests (if included): N/A (Phase I does not require tests)
- Services before endpoints: T008, T011 → T028-T030
- Endpoints/integration: T028-T031
- Story complete before moving to next priority: All tasks in US4 phase complete

### User Story 5 (Mark Task Complete)
- Tests (if included): N/A (Phase I does not require tests)
- Services before endpoints: T008, T011 → T032-T034
- Endpoints/integration: T032-T035
- Story complete before moving to next priority: All tasks in US5 phase complete

### Within Each Phase

- **Setup (Phase 1)**: T001-T006 (T003-T005 can run in parallel)
- **Foundational (Phase 2)**: T007-T011 (T008-T010 can run in parallel, T009 runs after T007-T008)
- **User Stories**: Each story's implementation tasks can run in parallel within the story
- **Integration (Phase 8)**: T036-T040 (sequential as they integrate components)
- **Polish (Phase 9)**: T041-T045 can run in parallel

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel: T003, T004, T005
- Foundational tasks T008, T010 can run in parallel (after T007)
- All tasks within each User Story can run in parallel: T013-T017 (US1), T018-T021 (US2), T022-T027 (US3), T028-T031 (US4), T032-T035 (US5)
- Polish tasks T041, T042, T043, T045 can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (List Tasks)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Deploy/demo if ready (Phase I is console app - just run python main.py)

**MVP delivers**: Users can create tasks and view their list. This is a complete, functional todo application.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Add Task) → Test independently → MVP Level 1
3. Add User Story 2 (List Tasks) → Test independently → MVP Level 2
4. Add User Story 5 (Mark Complete) → Test independently → MVP Level 3
5. Add User Story 3 (Update Task) → Test independently → MVP Level 4
6. Add User Story 4 (Delete Task) → Test independently → MVP Level 5
7. Complete Integration (Phase 8) → Full application
8. Polish (Phase 9) → Production-ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add Task) + Integration
   - Developer B: User Story 2 (List Tasks)
   - Developer C: User Story 5 (Mark Task Complete)
3. Stories complete and integrate independently
4. Team adds User Stories 3 and 4
5. Integration phase combines all work

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tasks are sequential within phases for logical ordering
- Verify tests fail before implementing (not applicable for Phase I)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are OPTIONAL for Phase I (not required by specification)
