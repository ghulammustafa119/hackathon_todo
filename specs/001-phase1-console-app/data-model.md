# Data Model: Phase I - In-Memory Console Todo App

**Feature**: [spec.md](./spec.md)
**Phase**: I
**Generated**: 2026-01-02

## Entities

### Task

**Description**: Represents a todo item with unique identifier, title, description, and completion status.

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|--------|------|----------|-----------|-------------|
| id | int | Yes | Auto-assigned | Unique integer identifier for the task |
| title | str | Yes | N/A | Non-empty string describing the task |
| description | str | No | None | Optional detailed description of the task |
| completed | bool | Yes | false | Completion status of the task |

**Relationships**: None (single entity for Phase I)

## Validation Rules

### Task Creation

- **title**: Must be non-empty string after stripping whitespace
- **description**: Optional, accepts any string value (including empty)
- **id**: Automatically assigned as unique integer, starts from 1, increments for each new task
- **completed**: Automatically set to false on creation

### Task Update

- **task_id**: Must exist in storage (positive integer)
- **title**: If provided, must be non-empty string
- **description**: Optional, accepts any string value
- **completed**: Cannot be updated via Update operation (use Mark Complete instead)

### Task Deletion

- **task_id**: Must exist in storage (positive integer)

### Task Completion Toggle

- **task_id**: Must exist in storage (positive integer)
- **completed**: Toggles between true and false

### Task Listing

- No validation required (retrieves all tasks)

## State Transitions

### Completion Status

| Current State | Operation | Next State |
|--------------|-----------|-------------|
| false (not completed) | Mark Complete | true |
| true (completed) | Mark Complete | false |

### Update Operation

- title: Can change from any value to any non-empty string
- description: Can change from any value to any string (including empty)
- completed: No transition allowed via Update operation

## Data Structure (In-Memory Storage)

### Task Representation

```python
Task = {
    "id": int,              # Unique identifier
    "title": str,            # Non-empty title
    "description": str | None, # Optional description
    "completed": bool          # Completion status
}
```

### Storage Container

```python
task_store: Dict[int, Task] = {}
# Key: task_id (int)
# Value: Task dict with id, title, description, completed
```

### Task List

```python
tasks: List[Task] = []
# List of Task dictionaries for display
# Maintains insertion order (no sorting required for Phase I)
```

## ID Generation Strategy

### Auto-Incrementing

```python
next_task_id: int = 1

def get_next_id() -> int:
    global next_task_id
    task_id = next_task_id
    next_task_id += 1
    return task_id
```

### Validation

- Ensures uniqueness (sequential assignment)
- Prevents ID collision (single-threaded, no deletion of ID reuse)

## In-Memory Constraints

### Phase I Scope

- All task data exists only during runtime
- No persistence to disk, database, or external storage
- Data lost on program termination (acceptable per Phase I specification)
- No serialization or deserialization required

### Thread Safety

- Single-threaded operation only (no async, no background threads)
- No concurrent access concerns (Phase I constraint)

### Performance Considerations

- Task lookup: O(1) via dict key access
- Task listing: O(n) iteration over all tasks
- Task creation: O(1) dict insertion
- Task deletion: O(1) dict deletion

## Edge Cases

### Empty Storage

- `get_all()` returns empty list
- Listing displays "No tasks found" message

### Invalid Task ID

- `get(task_id)` returns None for non-existent IDs
- Update/Delete/Complete operations return error for invalid IDs

### Large Task List

- No pagination required (Phase I specification)
- All tasks displayed in single output

### Whitespace Handling

- Title: Stripped before validation
- Empty title: Rejected (whitespace only considered empty)

## Migration Notes

### Phase I → Phase II

When transitioning to Phase II (web app + database):
- Replace in-memory dict with database table
- ID generation: Use database auto-increment or UUID
- Add persistence layer for create/update/delete operations
- Validation: Add database constraints (unique ID, not null title)
