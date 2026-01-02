# TaskDeletionSkill

## Description
This skill deletes a todo task from the in-memory store during Phase I. It ensures the task identifier exists before removal.

## Purpose
Provides task deletion functionality for the todo list console application, ensuring safe removal of tasks from the in-memory store.

## Responsibilities

### Core Operations
- **Validate Task ID**: Confirm task exists before attempting deletion
- **Delete Task**: Remove task from in-memory store
- **Confirm Removal**: Verify deletion succeeded

### Input Parameters (Required)
- `task_id` (str): The unique identifier of the task to delete

### Output
- Returns `success` (bool): True if deletion succeeded
- Returns `deleted_task` (dict | None): The task data that was deleted
- Returns `error` (str | None): Error message if deletion failed

### Validation Rules
- Task ID must exist in the in-memory store
- Only delete if task exists

## What This Skill Does NOT Handle

- ❌ User interaction/prompts (pre-validated input expected)
- ❌ Output rendering/display (handled by presentation layer)
- ❌ Confirmation dialogs (assumed handled before calling)
- ❌ Undo/restore functionality (not required in Phase I)
- ❌ Cascading deletions (no dependencies in Phase I)

## When to Use

Invoke this skill when:
- User requests to delete a task
- Task ID has been collected and validated
- The task needs to be permanently removed

## Workflow

```
1. Validate task_id exists via InMemoryStoreSkill.get()
2. If task not found, return error
3. Store task data for confirmation response
4. Call InMemoryStoreSkill.delete(task_id)
5. Return success confirmation with deleted task data
```

## Example Usage

```
Input:
{
  "task_id": "task-001"
}

Action: Invoke TaskDeletionSkill
Process:
  - Validate: Task "task-001" exists
  - Store: {"id": "task-001", "title": "Buy groceries", ...}
  - Delete: Call InMemoryStoreSkill.delete("task-001")
  - Return: Success with deleted task data

Output:
{
  "success": true,
  "deleted_task": {
    "id": "task-001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "created_at": "2026-01-02T14:30:00Z",
    "priority": "high",
    "tags": []
  }
}
```

## Error Scenarios

```
Input: {"task_id": "nonexistent-id"}
Output: {
  "success": false,
  "deleted_task": null,
  "error": "Task 'nonexistent-id' not found"
}

Input: {}  // Missing task_id
Output: {
  "success": false,
  "deleted_task": null,
  "error": "task_id is required"
}
```

## Phase I Constraints

- No undo/restore functionality
- No confirmation dialogs (handled by CLI layer)
- No audit logging
- No cascading deletes or dependency management
- Permanent deletion (no soft delete)

## Dependencies

- **InMemoryStoreSkill**: Required for task retrieval and deletion operations

## Error Handling

- If task_id not provided: Return clear error message
- If task_id not found: Return clear error message with success=false
- If InMemoryStoreSkill.delete() fails: Propagate the error

## Safety Considerations

- Always validate task exists before deletion
- Return deleted task data for user confirmation
- No partial deletion states (atomic operation)
