# Todo Evolution Project

A 5-phase evolution of a Todo List Manager, demonstrating Spec-Driven Development (SDD) principles.

## Project Overview

This project implements a Todo List Manager that evolves through 5 phases, from a simple console application to a cloud-native, event-driven system.

### Phases

| Phase | Description | Status |
|-------|-------------|--------|
| I | In-Memory Console Application | ✅ Complete |
| II | Web Application with File Persistence | Planned |
| III | AI Chatbot Integration | Planned |
| IV | Kubernetes Deployment | Planned |
| V | Cloud-Native with Event-Driven Architecture | Planned |

## Phase I - In-Memory Console Todo App

A console-based Todo List Manager with in-memory storage.

### Features

- Add new tasks with title and optional description
- List all tasks with completion status
- Update task title and description
- Delete tasks
- Mark tasks as complete/incomplete
- Menu-driven interface with input validation

### Installation

```bash
# No external dependencies required
# Requires Python 3.11+
```

### Running the Application

```bash
python todo_console/main.py
```

### Usage

1. Run the application
2. Choose from the menu:
   - 1: Add Task
   - 2: Update Task
   - 3: Delete Task
   - 4: List Tasks
   - 5: Mark Task as Complete
   - 6: Exit
3. Follow the prompts for each operation

### Project Structure

```
todo_console/
├── __init__.py
├── main.py                 # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py            # Task data model
├── services/
│   ├── __init__.py
│   ├── storage.py         # In-memory task storage
│   └── operations.py      # Business logic layer
└── cli/
    ├── __init__.py
    ├── input.py           # Input validation
    ├── menu.py            # Menu display and navigation
    └── render.py          # Console output rendering
```

### Governance

All code follows Spec-Driven Development principles:
- Code generated from specifications only
- Manual coding prohibited
- Constitution-first governance
- All phases must comply with project constitution

### Specification

See the full specification at [specs/001-phase1-console-app/spec.md](specs/001-phase1-console-app/spec.md)

### Architecture

**Separation of Concerns:**

- **Models**: Data structures (Task dataclass)
- **Services**: Business logic and storage (TaskStorage, TaskOperations)
- **CLI**: User interface (MainMenu, ConsoleRenderer, InputValidator)

**Data Model:**

```python
Task:
  - id: int (unique identifier)
  - title: str (required)
  - description: str | None (optional)
  - completed: bool (default: False)
```

**Storage:**

- In-memory dictionary: `Dict[int, Task]`
- Auto-incrementing task IDs starting from 1
- No persistence (Phase I only)

### Contributing

This project follows Spec-Driven Development:
1. All features must start with specification (`/sp.specify`)
2. Planning before implementation (`/sp.plan`)
3. Tasks generated from plan (`/sp.tasks`)
4. Implementation executed via `/sp.implement`

### License

Spec-Driven Development - Internal Project

---

**Built with Spec-Driven Development principles**
**Constitution-first governance**
**Python 3.11+**
