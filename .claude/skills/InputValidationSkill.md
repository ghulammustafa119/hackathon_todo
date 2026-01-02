# InputValidationSkill

## Description
This skill validates user-provided input during Phase I. It checks for empty values, invalid task identifiers, and unsupported actions.

## Purpose
Provides input validation as the first line of defense for the todo list console application, ensuring all user input meets minimum requirements before processing.

## Responsibilities

### Core Operations
- **Validate Task IDs**: Check task_id format and existence
- **Validate Required Fields**: Ensure required fields are present and non-empty
- **Validate Enum Values**: Check status, priority values against allowed options
- **Validate Actions**: Verify requested action is supported
- **Detect Invalid Input**: Identify malformed or unexpected input

### Validation Rules

#### Task ID Validation
- Must be non-empty string
- Must exist in in-memory store (if checking existence)
- Format: alphanumeric with optional hyphens/underscores

#### Required Field Validation
- Task title: non-empty string, max 200 characters
- Task description: optional string, max 500 characters
- Due date: valid ISO-8601 format if provided

#### Enum Value Validation
- Status: "pending", "in_progress", "completed"
- Priority: "low", "medium", "high"

#### Action Validation
- Supported actions: "create", "list", "update", "delete", "complete", "toggle"
- Action must be recognized and supported

### Input Parameters (Required)
- `action` (str): The action to validate
- `input_data` (dict): The user-provided input data

### Output
- Returns `valid` (bool): True if all validations pass
- Returns `errors` (list[str]): List of validation error messages
- Returns `sanitized_input` (dict | None): Sanitized input data if valid, null if invalid

## What This Skill Does NOT Handle

- ❌ Business logic validation (e.g., due date in past)
- ❌ State changes (no modifications to data)
- ❌ User interaction (no prompts for corrections)
- ❌ Cross-field validation (e.g., start_date < end_date)
- ❌ Complex validation rules (beyond Phase I scope)

## When to Use

Invoke this skill BEFORE any other skills:
- Before TaskCreationSkill
- Before TaskUpdateSkill
- Before TaskDeletionSkill
- Before TaskCompletionSkill
- Before TaskListingSkill (though minimal validation needed)

## Validation Workflow

```
1. Validate action is supported
2. Validate required fields for action
3. Validate field formats (strings, enums, dates)
4. If task_id provided, validate format and existence
5. If errors found, return valid=false with error list
6. If no errors, return valid=true with sanitized input
```

## Example Usage

### Valid Input Example

```
Input:
{
  "action": "create",
  "input_data": {
    "title": "Buy groceries",
    "priority": "high"
  }
}

Action: Invoke InputValidationSkill
Process:
  - Action "create" is supported ✓
  - Title "Buy groceries" is non-empty ✓
  - Priority "high" is valid enum ✓
  - No errors found

Output:
{
  "valid": true,
  "errors": [],
  "sanitized_input": {
    "title": "Buy groceries",
    "priority": "high"
  }
}
```

### Invalid Input Examples

#### Empty Required Field
```
Input:
{
  "action": "create",
  "input_data": {
    "title": ""
  }
}

Output:
{
  "valid": false,
  "errors": ["Task title cannot be empty"],
  "sanitized_input": null
}
```

#### Invalid Task ID
```
Input:
{
  "action": "update",
  "input_data": {
    "task_id": "nonexistent-123",
    "title": "Updated title"
  }
}

Output:
{
  "valid": false,
  "errors": ["Task ID 'nonexistent-123' not found"],
  "sanitized_input": null
}
```

#### Unsupported Action
```
Input:
{
  "action": "archive",
  "input_data": {}
}

Output:
{
  "valid": false,
  "errors": ["Action 'archive' is not supported"],
  "sanitized_input": null
}
```

#### Invalid Enum Value
```
Input:
{
  "action": "update",
  "input_data": {
    "task_id": "task-001",
    "status": "done"  // Invalid enum
  }
}

Output:
{
  "valid": false,
  "errors": ["Status must be 'pending', 'in_progress', or 'completed'"],
  "sanitized_input": null
}
```

## Validation by Action

### Create Action
- Required: `title` (non-empty)
- Optional: `description`, `due_date`, `priority`, `tags`
- Validations:
  - Title length ≤ 200
  - Description length ≤ 500 if provided
  - Due date is ISO-8601 if provided
  - Priority is valid enum if provided

### Update Action
- Required: `task_id` (exists in store)
- Optional: `title`, `description`, `due_date`, `priority`, `tags`, `status`
- Validations:
  - At least one field to update
  - Task ID exists
  - All enum values valid

### Delete Action
- Required: `task_id` (exists in store)
- Validations:
  - Task ID exists

### Complete/Toggle Action
- Required: `task_id` (exists in store)
- Optional: `status` (if provided, must be valid enum)
- Validations:
  - Task ID exists
  - Status is valid enum if provided

### List Action
- No parameters required
- No validation needed (always valid)

## Error Message Format

All error messages should be:
- Clear and specific
- User-friendly (avoid technical jargon)
- Indicate exactly what's wrong
- Suggest corrections when possible

Examples:
- "Task title cannot be empty"
- "Task ID 'xyz' not found"
- "Status must be 'pending', 'in_progress', or 'completed'"
- "Due date must be in ISO-8601 format (e.g., 2026-01-02)"

## Phase I Constraints

- Minimal validation only (not comprehensive)
- No business rule validation
- No cross-field validation
- No custom validation rules
- Static validation rules only

## Dependencies

- **InMemoryStoreSkill**: Required to check task_id existence

## Error Handling

- Return `valid: false` for any validation failure
- Accumulate all errors (don't stop on first error)
- Return empty `errors` list for valid input
- Return `sanitized_input: null` for invalid input

## Integration with Other Skills

This skill should be called FIRST before any other skill:
```
InputValidationSkill → (other skills if valid)
```

If validation fails, do not proceed to other skills. Return validation errors to user.

## Sanitization

If input is valid, `sanitized_input` contains:
- Trimmed strings (whitespace removed)
- Normalized enum values (lowercase, standardized)
- Validated fields only

Example:
```
Input: {"title": "  Buy groceries  ", "priority": "HIGH"}
Sanitized: {"title": "Buy groceries", "priority": "high"}
```
