# Phase I: In-Memory Python Console Todo App

A command-line todo application that stores tasks in memory, built using Claude Code and Spec-Kit Plus.

## Features

- **Add Task** – Create new todo items with title and description
- **Update Task** – Modify existing task title or description
- **Delete Task** – Remove tasks permanently
- **View Task List** – Display all tasks with status indicators
- **Mark as Complete** – Toggle task completion status

## Technology Stack

- Python 3.13+
- UV (package manager)

## Setup & Run

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project
cd todo_console

# Run the app
uv run python -m todo_console.main
```

## Project Structure

```
todo_console/
├── main.py                 # Entry point
├── __init__.py
├── pyproject.toml          # UV/Python config
├── models/
│   └── task.py             # Task dataclass
├── services/
│   ├── storage.py          # In-memory storage
│   └── operations.py       # CRUD operations
├── cli/
│   ├── menu.py             # Menu system
│   ├── render.py           # Console output
│   └── input.py            # Input validation
└── tests/
    └── test_task_operations.py
```

## Running Tests

```bash
uv run pytest tests/
```
