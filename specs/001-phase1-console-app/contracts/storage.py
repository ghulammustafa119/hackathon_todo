# Storage Service Contract

## Purpose

Internal contract for in-memory task storage operations.

## Class: TaskStorage

Manages in-memory storage of tasks with unique integer IDs.

### Methods

#### `__init__(self) -> None`

Initialize empty in-memory task storage.

**Returns**: None

**Side Effects**: Creates empty dictionary for task storage

---

#### `create(self, title: str, description: str = None) -> int`

Create a new task with specified title and optional description.

**Parameters**:
- `title` (str, required): Non-empty task title
- `description` (str, optional): Task description details

**Returns**: int - Unique task ID assigned to created task

**Side Effects**:
- Adds task to internal storage with unique ID
- Increments ID counter
- Sets `completed` to `false` for new task

**Raises**:
- ValueError: If `title` is empty or whitespace only

---

#### `get(self, task_id: int) -> Optional[Task]`

Retrieve a single task by ID.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to retrieve

**Returns**: Optional[Task] - Task dict if found, None if not found

**Side Effects**: None (read operation)

---

#### `get_all(self) -> List[Task]`

Retrieve all tasks in storage.

**Returns**: List[Task] - List of all task dicts

**Side Effects**: None (read operation)

---

#### `update(self, task_id: int, title: str = None, description: str = None) -> bool`

Update an existing task's title and/or description.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to update
- `title` (str, optional): New title value
- `description` (str, optional): New description value

**Returns**: bool - True if update succeeded, False if task not found

**Side Effects**:
- Updates task in storage
- Does NOT modify `completed` status

**Raises**:
- ValueError: If neither `title` nor `description` provided

---

#### `delete(self, task_id: int) -> bool`

Delete a task from storage.

**Parameters**:
- `task_id` (int, required): Unique identifier of task to delete

**Returns**: bool - True if deletion succeeded, False if task not found

**Side Effects**:
- Removes task from storage
- Task ID is NOT reused

---

#### `exists(self, task_id: int) -> bool`

Check if a task ID exists in storage.

**Parameters**:
- `task_id` (int, required): Unique identifier to check

**Returns**: bool - True if task exists, False if not found

**Side Effects**: None (read operation)

## Data Structure

### Task Dict

```python
Task = {
    "id": int,           # Unique identifier
    "title": str,         # Non-empty title
    "description": str,   # Optional description or None
    "completed": bool      # Completion status
}
```

### Storage Structure

```python
Dict[int, Task]  # Key: task_id, Value: Task dict
```

## Performance

- `create`: O(1) - dictionary insertion
- `get`: O(1) - dictionary key lookup
- `get_all`: O(n) - iteration over all tasks
- `update`: O(1) - dictionary key lookup and update
- `delete`: O(1) - dictionary key deletion
- `exists`: O(1) - dictionary key existence check

## Constraints

- In-memory only (no persistence)
- Single-threaded (no async operations)
- No ID reuse after deletion
- Unique ID assignment guaranteed
