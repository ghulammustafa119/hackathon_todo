# ConsoleRenderSkill

## Description
This skill handles all console output rendering for the Phase I todo application. It displays menus, task lists, success messages, and error messages in a clear and consistent format.

## Purpose
Provides consistent, user-friendly console output for all application interactions in the todo list console application.

## Responsibilities

### Core Operations
- **Render Menus**: Display main menu and action options
- **Render Task Lists**: Format and display task data
- **Render Success Messages**: Display confirmation messages
- **Render Error Messages**: Display error information clearly
- **Render Prompts**: Display user prompts for input

### Output Format Guidelines

#### Consistent Formatting
- Use clear section headers
- Maintain consistent indentation
- Provide visual separation between sections
- Use meaningful visual indicators (checkmarks, X marks, etc.)

#### Visual Indicators
- ✓ (checkmark) for success/confirmation
- ✗ (X mark) for errors
- → (arrow) for navigation
- • (bullet) for lists
- ◆ (diamond) for menu items

### Output Categories

#### 1. Main Menu
```
┌─────────────────────────────┐
│     TODO LIST MANAGER       │
└─────────────────────────────┘

Available Actions:
  ◆ 1. Add new task
  ◆ 2. List all tasks
  ◆ 3. Update task
  ◆ 4. Delete task
  ◆ 5. Mark task as complete
  ◆ 6. Exit

Enter your choice (1-6):
```

#### 2. Task List Display
```
┌─────────────────────────────┐
│         YOUR TASKS          │
└─────────────────────────────┘

[task-001] Buy groceries
  Status: ⏳ Pending
  Priority: 🔴 High
  Tags: (none)
  Created: 2026-01-02 14:30

[task-002] Write report
  Status: ✓ Completed
  Priority: 🟡 Medium
  Tags: work
  Created: 2026-01-01 09:00

Total: 2 tasks
```

#### 3. Success Messages
```
✓ Task created successfully
  Task ID: task-001
  Title: Buy groceries
```

```
✓ Task deleted successfully
  Task ID: task-001
```

#### 4. Error Messages
```
✗ Error: Task not found
  Task ID: xyz
  Please check the ID and try again.
```

```
✗ Error: Task title cannot be empty
  Please provide a valid task title.
```

#### 5. Input Prompts
```
→ Task title: [user types here]
→ Task description (optional): [user types here]
→ Priority (low/medium/high) [default: medium]: [user types here]
```

### Input Parameters

#### Render Menu
```python
{
  "type": "menu",
  "title": str,
  "options": list[dict]  # [{"key": "1", "label": "Add task"}, ...]
}
```

#### Render Task List
```python
{
  "type": "task_list",
  "tasks": list[dict],  # List of task objects
  "title": str  # Optional title override
}
```

#### Render Success Message
```python
{
  "type": "success",
  "message": str,
  "details": dict  # Optional key-value details
}
```

#### Render Error Message
```python
{
  "type": "error",
  "message": str,
  "details": str | None  # Optional error details
}
```

#### Render Prompt
```python
{
  "type": "prompt",
  "message": str,
  "default": str | None  # Optional default value
}
```

### Output
- Prints formatted output to console
- Returns None (output is side effect)

## What This Skill Does NOT Handle

- ❌ User input collection (use CLI interaction layer)
- ❌ State modifications (read-only)
- ❌ Business logic (presentation only)
- ❌ Input validation (validate before calling)
- ❌ Color/terminal control codes (plain text only for Phase I)

## When to Use

Invoke this skill for ALL console output:
- After any action completes (success/error)
- Before user input is requested (prompts)
- When displaying task data (task lists)
- When showing menu options
- For any user-facing communication

## Rendering Workflow

```
1. Receive data from caller (task list, message, etc.)
2. Select appropriate format template
3. Format data according to template
4. Print formatted output to console
```

## Example Usage

### Display Task List
```
Input:
{
  "type": "task_list",
  "tasks": [
    {
      "id": "task-001",
      "title": "Buy groceries",
      "status": "pending",
      "priority": "high",
      "tags": []
    }
  ]
}

Action: Invoke ConsoleRenderSkill
Output:
┌─────────────────────────────┐
│         YOUR TASKS          │
└─────────────────────────────┘

[task-001] Buy groceries
  Status: ⏳ Pending
  Priority: 🔴 High
  Tags: (none)
  Created: 2026-01-02 14:30

Total: 1 tasks
```

### Display Success Message
```
Input:
{
  "type": "success",
  "message": "Task created successfully",
  "details": {
    "Task ID": "task-001",
    "Title": "Buy groceries"
  }
}

Action: Invoke ConsoleRenderSkill
Output:
✓ Task created successfully
  Task ID: task-001
  Title: Buy groceries
```

### Display Error Message
```
Input:
{
  "type": "error",
  "message": "Task not found",
  "details": "Task ID: xyz"
}

Action: Invoke ConsoleRenderSkill
Output:
✗ Error: Task not found
  Task ID: xyz
  Please check the ID and try again.
```

### Display Menu
```
Input:
{
  "type": "menu",
  "title": "TODO LIST MANAGER",
  "options": [
    {"key": "1", "label": "Add new task"},
    {"key": "2", "label": "List all tasks"},
    {"key": "3", "label": "Exit"}
  ]
}

Action: Invoke ConsoleRenderSkill
Output:
┌─────────────────────────────┐
│     TODO LIST MANAGER       │
└─────────────────────────────┘

Available Actions:
  ◆ 1. Add new task
  ◆ 2. List all tasks
  ◆ 3. Exit

Enter your choice (1-3):
```

## Empty Task List

```
┌─────────────────────────────┐
│         YOUR TASKS          │
└─────────────────────────────┘

No tasks found. Create your first task!

```

## Status Indicator Mapping

- "pending" → "⏳ Pending"
- "in_progress" → "🔄 In Progress"
- "completed" → "✓ Completed"

## Priority Indicator Mapping

- "low" → "🟢 Low"
- "medium" → "🟡 Medium"
- "high" → "🔴 High"

## Phase I Constraints

- Plain text output only (no colors, no terminal control codes)
- Simple ASCII art/box drawing characters only
- No rich formatting (bold, underline, etc.)
- No clearing screen or cursor manipulation
- Simple, readable output for console

## Dependencies

- None (pure presentation layer)

## Error Handling

- This skill assumes valid input data
- If data is malformed, render with placeholder values
- Never raises exceptions (graceful degradation)

## Design Principles

1. **Clarity**: Output should be immediately understandable
2. **Consistency**: Use same formatting across all displays
3. **Conciseness**: Avoid unnecessary verbosity
4. **Hierarchy**: Use visual indicators to show importance
5. **Actionability**: Make next steps clear

## Best Practices

- Always show task ID in task lists
- Always include clear success/error indicators
- Use blank lines for visual separation
- Align related information vertically
- Provide total counts for lists
