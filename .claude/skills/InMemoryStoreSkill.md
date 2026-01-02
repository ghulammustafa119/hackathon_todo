# InMemoryStoreSkill

## Description
This skill manages the in-memory storage of todo tasks for Phase I. It maintains the single source of truth for all tasks using Python data structures only.

## Purpose
Provides centralized task state management for the todo list console application. All task data lives in memory during runtime.

## Responsibilities

### Core Operations
- **Create**: Add new tasks with unique identifiers
- **Read**: Retrieve tasks by ID or query/filter
- **Update**: Modify task properties (status, title, etc.)
- **Delete**: Remove tasks from memory

### Data Model
```python
Task structure:
{
    "id": "unique_id",           # str: UUID or sequential ID
    "title": "task_title",       # str: Required task name
    "description": "desc",       # str: Optional details
    "status": "pending",         # str: pending | in_progress | completed
    "created_at": "ISO-8601",    # str: Creation timestamp
    "due_date": "ISO-8601",      # str: Optional due date
    "priority": "medium",        # str: low | medium | high
    "tags": ["tag1", "tag2"]     # list[str]: Optional tags
}
```

### Storage Implementation
- Uses Python `dict` as primary storage (task_id → task_data)
- Maintains task ID generation (sequential or UUID)
- Thread-safe operations for single-threaded console app

## What This Skill Does NOT Handle

- ❌ User input collection (handled by CLI interaction)
- ❌ Output rendering/display (handled by presentation layer)
- ❌ File persistence/JSON export (handled by persistence layer if needed)
- ❌ Business logic/validation beyond storage constraints

## When to Use

Invoke this skill whenever task state needs to be manipulated:
- Creating a new task
- Updating task status or properties
- Deleting tasks
- Querying/filtering tasks
- Listing all tasks

## Example Usage

```
Task: "Add a new task called 'Buy groceries'"
Action: Invoke InMemoryStoreSkill.create(title="Buy groceries", ...)
Result: Returns task_id and stores task in memory

Task: "Mark task #123 as completed"
Action: Invoke InMemoryStoreSkill.update(task_id="123", status="completed")
Result: Updates task in memory, returns success
```

## Phase I Constraints

- Data lives in memory only (Python data structures)
- No external databases
- No ORM or persistence libraries
- Simple, transparent data structures

## API Contract (Conceptual)

```python
class InMemoryTaskStore:
    def create(self, title: str, **kwargs) -> str: ...
    def get(self, task_id: str) -> dict | None: ...
    def update(self, task_id: str, **kwargs) -> bool: ...
    def delete(self, task_id: str) -> bool: ...
    def list_all(self) -> list[dict]: ...
    def filter_by_status(self, status: str) -> list[dict]: ...
```
