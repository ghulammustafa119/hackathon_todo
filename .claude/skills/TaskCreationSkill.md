# TaskCreationSkill

## Description
This skill creates new todo tasks according to Phase I specifications. It accepts validated task details, assigns a unique identifier, sets the default completion status, and stores the task using the in-memory store.

## Purpose
Provides task creation functionality for the todo list console application, ensuring all tasks are properly initialized and stored.

## Responsibilities

### Core Operations
- **Assign Unique ID**: Generate a unique identifier for each new task
- **Set Default Status**: Initialize tasks with "pending" status
- **Set Timestamps**: Record creation time (ISO-8601 format)
- **Store Task**: Persist task to in-memory store via InMemoryStoreSkill

### Input Parameters (Required)
- `title` (str): The task title/name
- `description` (str): Optional task description

### Input Parameters (Optional)
- `due_date` (str): ISO-8601 formatted due date
- `priority` (str): "low", "medium", or "high" (default: "medium")
- `tags` (list[str]): List of tags for categorization

### Output
- Returns `task_id` (str) of the newly created task
- Returns task data dict for confirmation

### Default Values
- `status`: "pending" (all new tasks start as pending)
- `created_at`: Current timestamp (ISO-8601)
- `priority`: "medium" (if not specified)
- `tags`: [] (empty list if not specified)

## What This Skill Does NOT Handle

- ❌ Input validation (handled by CLI interaction layer before calling)
- ❌ User interaction/prompts (pre-validated input expected)
- ❌ Duplicate title checking (not required in Phase I)
- ❌ Business rules (e.g., due date validation, tag limits)

## When to Use

Invoke this skill when:
- User requests to create a new task
- Task details have been collected and validated
- The task needs to be stored in the in-memory store

## Workflow

```
1. Input validated task details (from CLI interaction)
2. Generate unique task ID (sequential or UUID)
3. Set default values (status="pending", created_at=now)
4. Call InMemoryStoreSkill.create() with full task data
5. Return task_id and confirmation
```

## Example Usage

```
Input:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high"
}

Action: Invoke TaskCreationSkill
Process:
  - Generate ID: "task-001"
  - Set status: "pending"
  - Set created_at: "2026-01-02T14:30:00Z"
  - Store via InMemoryStoreSkill

Output:
{
  "task_id": "task-001",
  "task": {
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

## Phase I Constraints

- No external ID generation services
- No validation logic (assumes pre-validated input)
- No complex business rules
- Simple, straightforward task creation

## Dependencies

- **InMemoryStoreSkill**: Required for storing the created task

## Error Handling

- If InMemoryStoreSkill fails, propagate the error
- Return clear error message if required fields are missing
