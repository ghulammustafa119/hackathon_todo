# TaskCompletionSkill

## Description
This skill toggles the completion status of a todo task during Phase I. It ensures the task state is updated consistently in the in-memory store.

## Purpose
Provides task completion functionality for the todo list console application, allowing users to mark tasks as completed or revert them to pending status.

## Responsibilities

### Core Operations
- **Validate Task ID**: Confirm task exists before toggling status
- **Toggle Status**: Switch between "pending" and "completed" (or optionally "in_progress")
- **Persist Change**: Update task in in-memory store

### Input Parameters (Required)
- `task_id` (str): The unique identifier of the task to toggle

### Input Parameters (Optional)
- `status` (str): Explicitly set status to one of: "pending", "in_progress", "completed"
  - If not provided, toggle between current status and "completed"

### Output
- Returns `success` (bool): True if toggle succeeded
- Returns `updated_task` (dict): The task with updated status
- Returns `old_status` (str): The status before the change
- Returns `error` (str | None): Error message if toggle failed

### Status Transitions
- If no status provided: Toggle between "pending" ↔ "completed"
- If status provided: Set to specified value directly
- From "in_progress": Can transition to "pending" or "completed"
- From "completed": Can transition to "pending" or "in_progress"
- From "pending": Can transition to "in_progress" or "completed"

### Default Toggle Logic
```python
if current_status == "pending":
    new_status = "completed"
elif current_status == "completed":
    new_status = "pending"
elif current_status == "in_progress":
    new_status = "completed"  # Mark in-progress as completed
```

## What This Skill Does NOT Handle

- ❌ User input handling (pre-validated task_id expected)
- ❌ Output formatting (handled by presentation layer)
- ❌ Business logic like auto-archiving completed tasks
- ❌ Progress tracking or reporting

## When to Use

Invoke this skill when:
- User requests to mark a task as complete
- User requests to unmark a completed task
- User requests to set a specific status (pending/in_progress/completed)
- Task completion state needs to change

## Workflow

```
1. Validate task_id exists via InMemoryStoreSkill.get()
2. If task not found, return error
3. If status not provided, calculate new status based on current
4. Call InMemoryStoreSkill.update(task_id, status=new_status)
5. Return success with old and new status
```

## Example Usage

```
Input: {"task_id": "task-001"}  // Toggle mode

Action: Invoke TaskCompletionSkill
Process:
  - Get current task: status="pending"
  - Toggle: new_status = "completed"
  - Update: Call InMemoryStoreSkill.update("task-001", status="completed")

Output:
{
  "success": true,
  "updated_task": {
    "id": "task-001",
    "title": "Buy groceries",
    "status": "completed",
    ...
  },
  "old_status": "pending",
  "new_status": "completed"
}

---

Input: {"task_id": "task-001", "status": "pending"}  // Explicit status

Action: Invoke TaskCompletionSkill
Process:
  - Get current task: status="completed"
  - Set: new_status = "pending" (explicit)
  - Update: Call InMemoryStoreSkill.update("task-001", status="pending")

Output:
{
  "success": true,
  "updated_task": {...},
  "old_status": "completed",
  "new_status": "pending"
}
```

## Error Scenarios

```
Input: {"task_id": "nonexistent-id"}
Output: {
  "success": false,
  "updated_task": null,
  "error": "Task 'nonexistent-id' not found"
}

Input: {}  // Missing task_id
Output: {
  "success": false,
  "updated_task": null,
  "error": "task_id is required"
}

Input: {"task_id": "task-001", "status": "invalid"}
Output: {
  "success": false,
  "updated_task": null,
  "error": "Invalid status: must be 'pending', 'in_progress', or 'completed'"
}
```

## Phase I Constraints

- No validation beyond status enum
- No complex business rules for status transitions
- No notification or alerts on completion
- No automatic archiving of completed tasks

## Dependencies

- **InMemoryStoreSkill**: Required for task retrieval and update operations

## Error Handling

- If task_id not provided: Return clear error message
- If task_id not found: Return clear error message
- If status is invalid: Return clear error message
- If InMemoryStoreSkill.update() fails: Propagate the error

## Status Transition Table

| From      | Allowed To     |
|-----------|----------------|
| pending   | in_progress, completed |
| in_progress | pending, completed |
| completed | pending, in_progress |
