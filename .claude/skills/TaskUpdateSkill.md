# TaskUpdateSkill

## Description
This skill updates existing todo tasks during Phase I. It modifies task attributes such as title or description after validating the task identifier.

## Purpose
Provides task update functionality for the todo list console application, ensuring updates are applied to valid tasks in a controlled manner.

## Responsibilities

### Core Operations
- **Validate Task ID**: Confirm task exists before attempting updates
- **Apply Updates**: Modify specified task attributes
- **Delegated Storage**: Use InMemoryStoreSkill to persist changes

### Input Parameters (Required)
- `task_id` (str): The unique identifier of the task to update

### Input Parameters (Optional - at least one required)
- `title` (str): New task title
- `description` (str): New task description
- `due_date` (str): ISO-8601 formatted due date
- `priority` (str): "low", "medium", or "high"
- `tags` (list[str]): Replace existing tags with new list
- `status` (str): "pending", "in_progress", or "completed"

### Output
- Returns `success` (bool): True if update succeeded
- Returns `updated_task` (dict): The updated task data
- Returns `error` (str | None): Error message if update failed

### Validation Rules
- Task ID must exist in the in-memory store
- At least one updateable field must be provided
- Status must be one of: "pending", "in_progress", "completed"
- Priority must be one of: "low", "medium", "high"

## What This Skill Does NOT Handle

- ❌ Task storage management (delegates to InMemoryStoreSkill)
- ❌ User interaction/prompts (pre-validated input expected)
- ❌ Status transition validation (e.g., pending → completed allowed directly)
- ❌ History tracking of changes (not required in Phase I)

## When to Use

Invoke this skill when:
- User requests to modify an existing task
- Task ID and update data have been collected
- The update needs to be applied to a specific task

## Workflow

```
1. Validate task_id exists via InMemoryStoreSkill.get()
2. If task not found, return error
3. Prepare update dictionary with provided fields
4. Call InMemoryStoreSkill.update(task_id, **updates)
5. Return success confirmation and updated task data
```

## Example Usage

```
Input:
{
  "task_id": "task-001",
  "title": "Buy groceries - UPDATED",
  "priority": "high"
}

Action: Invoke TaskUpdateSkill
Process:
  - Validate: Task "task-001" exists
  - Prepare: {"title": "Buy groceries - UPDATED", "priority": "high"}
  - Update: Call InMemoryStoreSkill.update("task-001", title="...", priority="high")
  - Return: Success with updated task data

Output:
{
  "success": true,
  "updated_task": {
    "id": "task-001",
    "title": "Buy groceries - UPDATED",
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
Input: {"task_id": "nonexistent-id", "title": "New title"}
Output: {
  "success": false,
  "error": "Task 'nonexistent-id' not found"
}

Input: {"task_id": "task-001"}  // No fields to update
Output: {
  "success": false,
  "error": "At least one updateable field required"
}
```

## Phase I Constraints

- No audit logging of changes
- No validation of status transitions
- No history tracking
- Simple field-level updates only

## Dependencies

- **InMemoryStoreSkill**: Required for task retrieval and update operations

## Error Handling

- If task_id not found: Return clear error message
- If no updateable fields provided: Return clear error message
- If InMemoryStoreSkill.update() fails: Propagate the error
