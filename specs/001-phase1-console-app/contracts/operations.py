# Task Operations Service Contract

## Purpose

Orchestrates task CRUD operations with validation, using storage service for persistence.

## Class: TaskOperations

Business logic layer that coordinates task creation, updates, deletions, completion toggling, and listing.

### Methods

#### `__init__(self, storage: TaskStorage) -> None`

Initialize operations with storage dependency.

**Parameters**:
- `storage` (TaskStorage, required): Instance of TaskStorage service

**Returns**: None

**Side Effects**: Stores storage reference for task operations

---

#### `create_task(self, title: str, description: str = None) -> dict`

Create a new task with validation and ID assignment.

**Parameters**:
- `title` (str, required): Non-empty task title
- `description` (str, optional): Task description details

**Returns**: dict with keys:
- `success` (bool): True if task created, False if validation failed
- `task_id` (int): Assigned task ID (only if success=True)
- `task` (dict): Created task data (only if success=True)
- `error` (str | None): Error message (only if success=False)

**Side Effects**:
- Calls `storage.create()` with title, description
- Assigns unique task ID via storage

**Raises**: None (validation errors handled in return value)

---

#### `update_task(self, task_id: int, title: str = None, description: str = None) -> dict`

Update an existing task's title and/or description.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to update
- `title` (str, optional): New title value
- `description` (str, optional): New description value

**Returns**: dict with keys:
- `success` (bool): True if task updated, False if validation failed or not found
- `updated_task` (dict): Updated task data (only if success=True)
- `error` (str | None): Error message (only if success=False)

**Side Effects**:
- Calls `storage.exists()` to validate task_id
- Calls `storage.update()` if validation passes
- Does NOT modify task completion status

**Raises**: None (validation errors handled in return value)

---

#### `delete_task(self, task_id: int) -> dict`

Delete a task from storage.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to delete

**Returns**: dict with keys:
- `success` (bool): True if task deleted, False if not found
- `deleted_task` (dict | None): Deleted task data (only if success=True)
- `error` (str | None): Error message (only if success=False)

**Side Effects**:
- Calls `storage.exists()` to validate task_id
- Calls `storage.delete()` if validation passes
- Task permanently removed (no undo in Phase I)

**Raises**: None (validation errors handled in return value)

---

#### `toggle_completion(self, task_id: int) -> dict`

Toggle task completion status between false and true.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to toggle

**Returns**: dict with keys:
- `success` (bool): True if task toggled, False if not found
- `updated_task` (dict): Updated task data (only if success=True)
- `old_status` (bool): Previous completion status (only if success=True)
- `new_status` (bool): New completion status (only if success=True)
- `error` (str | None): Error message (only if success=False)

**Side Effects**:
- Calls `storage.exists()` to validate task_id
- Calls `storage.update()` to toggle completed status
- Performs boolean toggle: !completed

**Raises**: None (validation errors handled in return value)

---

#### `list_tasks(self) -> dict`

Retrieve all tasks for display.

**Parameters**: None

**Returns**: dict with keys:
- `success` (bool): Always True (list operation always succeeds)
- `tasks` (list): List of all task dicts
- `count` (int): Number of tasks in storage

**Side Effects**:
- Calls `storage.get_all()` to retrieve all tasks
- No validation required

**Raises**: None

## Business Logic Rules

### Create Task

1. Validate title is non-empty (via InputValidator)
2. Call storage.create() with title, description
3. Return success with assigned task_id

### Update Task

1. Validate task_id exists (via storage.exists())
2. If not found: return success=False with error
3. Validate at least one of title or description provided
4. Call storage.update() with provided fields
5. Return success with updated_task

### Delete Task

1. Validate task_id exists (via storage.exists())
2. If not found: return success=False with error
3. Call storage.delete() to remove task
4. Return success with deleted_task

### Toggle Completion

1. Validate task_id exists (via storage.exists())
2. If not found: return success=False with error
3. Retrieve current task via storage.get()
4. Toggle completed status: new_status = !task.completed
5. Call storage.update() with completed=new_status
6. Return success with old_status, new_status, updated_task

### List Tasks

1. Call storage.get_all() to retrieve all tasks
2. Return success with tasks list and count

## Error Handling

### Validation Errors

- Empty title in create_task: Return success=False, error="Title cannot be empty"
- Invalid task_id in update/delete/toggle: Return success=False, error="Task not found"

### Storage Errors

- Propagate any storage failures (should not occur with in-memory dict)

## Return Value Standards

### Success Response

```python
{
    "success": True,
    "task_id": 123,  # or None for non-ID operations
    "task": {...},  # or None for non-task operations
    "updated_task": {...},  # or None
    "old_status": False,  # or None
    "new_status": True,  # or None
    "error": None
}
```

### Error Response

```python
{
    "success": False,
    "task_id": None,
    "task": None,
    "updated_task": None,
    "error": "User-friendly error message"
}
```

## Dependencies

- **TaskStorage**: Required for all persistence operations
- **InputValidator**: Optional (can be external or inline)
