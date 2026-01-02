# TaskListingSkill

## Description
This skill retrieves all todo tasks from the in-memory store and prepares them for display. It does not perform sorting, filtering, or advanced formatting beyond Phase I requirements.

## Purpose
Provides task retrieval functionality for the todo list console application, allowing users to view all stored tasks.

## Responsibilities

### Core Operations
- **Retrieve All Tasks**: Fetch all tasks from in-memory store
- **Prepare for Display**: Format task data for presentation layer
- **Return Raw Data**: Provide unmodified task data to caller

### Input Parameters
- No required parameters for listing all tasks

### Output
- Returns `tasks` (list[dict]): List of all task objects
- Returns `count` (int): Total number of tasks
- Returns `error` (str | None): Error message if retrieval failed

### Task Data Format
Each task in the list contains the full task structure:
```python
{
    "id": "unique_id",
    "title": "task_title",
    "description": "task_description",
    "status": "pending|in_progress|completed",
    "created_at": "ISO-8601",
    "due_date": "ISO-8601" | None,
    "priority": "low|medium|high",
    "tags": ["tag1", "tag2"]
}
```

## What This Skill Does NOT Handle

- ❌ Sorting (tasks returned in storage order)
- ❌ Filtering (all tasks returned, no criteria)
- ❌ Grouping (no categorization by status, priority, etc.)
- ❌ Advanced formatting (no table/grid layouts, no color coding)
- ❌ Pagination (all tasks returned in single list)
- ❌ User interaction (no prompts, no input handling)

## When to Use

Invoke this skill when:
- User requests to view all tasks
- Application needs to display task list
- Any layer needs access to complete task data

## Workflow

```
1. Call InMemoryStoreSkill.list_all()
2. If retrieval fails, return error
3. Return raw task list with count
```

## Example Usage

```
Input: {}  // No parameters required

Action: Invoke TaskListingSkill
Process:
  - Retrieve: Call InMemoryStoreSkill.list_all()
  - Package: Return tasks with count

Output:
{
  "tasks": [
    {
      "id": "task-001",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2026-01-02T14:30:00Z",
      "priority": "high",
      "tags": []
    },
    {
      "id": "task-002",
      "title": "Write report",
      "description": "Q4 sales report",
      "status": "completed",
      "created_at": "2026-01-01T09:00:00Z",
      "priority": "medium",
      "tags": ["work"]
    }
  ],
  "count": 2
}
```

## Empty Store Scenario

```
Input: {}

Output:
{
  "tasks": [],
  "count": 0,
  "error": null
}
```

## Error Scenario

```
Input: {}

Output:
{
  "tasks": [],
  "count": 0,
  "error": "Failed to retrieve tasks from in-memory store"
}
```

## Phase I Constraints

- No sorting by any field (date, priority, status)
- No filtering (show all tasks regardless of status)
- No pagination limits
- No formatting applied (raw data only)
- Simple retrieval of all tasks in storage order

## Dependencies

- **InMemoryStoreSkill**: Required for retrieving tasks

## Use with Presentation Layer

The presentation layer (CLI interface) should:
- Iterate through the returned task list
- Apply any display formatting (text tables, line breaks, etc.)
- Add status indicators or visual cues as needed
- Handle empty list display (e.g., "No tasks found")

## Display Format (Presentation Layer Example)

The presentation layer might format the raw data as:

```
Tasks (2):
  [task-001] Buy groceries [pending] HIGH
  [task-002] Write report [completed] MEDIUM
```

This formatting is NOT done by TaskListingSkill.

## Error Handling

- If InMemoryStoreSkill.list_all() fails: Propagate the error with clear message
- If store is empty: Return empty list with count=0 (not an error)

## Performance Considerations

- O(n) operation where n = number of tasks
- All tasks loaded into memory
- No lazy loading or pagination in Phase I
