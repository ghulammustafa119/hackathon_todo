# Console Output Rendering Contract

## Purpose

Provides consistent, user-friendly console output formatting for all application interactions.

## Class: ConsoleRenderer

Formats and displays user-facing output including menus, task lists, success messages, and errors.

### Methods

#### `display_menu(self, title: str, options: List[str]) -> None`

Display main menu with title and numbered options.

**Parameters**:
- `title` (str, required): Menu heading/title
- `options` (list[str], required): List of menu option labels

**Returns**: None

**Side Effects**: Prints formatted menu to console

**Format**:
```
═════════════════════════════════
 {title}
═════════════════════════════════

{index + 1}. {option}
{index + 2}. {option}
...

Enter your choice (1-{len(options)}):
```

---

#### `display_task_list(self, tasks: List[Task]) -> None`

Display all tasks in readable format with ID, title, and completion status.

**Parameters**:
- `tasks` (list[dict], required): List of task dicts from storage

**Returns**: None

**Side Effects**: Prints formatted task list to console

**Format for Non-Empty List**:
```
─────────────────────────────────────────
 YOUR TASKS
─────────────────────────────────────────

Task ID {task['id']}: {task['title']}
  Status: {'✓ Completed' if task['completed'] else '⏳ Pending'}

Task ID {task['id']}: {task['title']}
  Status: {'✓ Completed' if task['completed'] else '⏳ Pending'}

─────────────────────────────────────────
Total: {count} tasks
```

**Format for Empty List**:
```
─────────────────────────────────────────
 YOUR TASKS
─────────────────────────────────────────

No tasks found. Create your first task!

─────────────────────────────────────────
```

---

#### `display_success(self, message: str) -> None`

Display success message for completed operations.

**Parameters**:
- `message` (str, required): Success message to display

**Returns**: None

**Side Effects**: Prints formatted success message to console

**Format**:
```
✓ Success: {message}
```

**With Details (dict parameter - optional)**:
```
✓ Success: {message}
  Key: Value
  Key: Value
```

---

#### `display_error(self, message: str) -> None`

Display error message for failed operations.

**Parameters**:
- `message` (str, required): Error message to display

**Returns**: None

**Side Effects**: Prints formatted error message to console

**Format**:
```
✗ Error: {message}
```

**With Details (dict parameter - optional)**:
```
✗ Error: {message}
  Detail: Additional information
```

---

#### `display_prompt(self, prompt: str) -> None`

Display input prompt for user data collection.

**Parameters**:
- `prompt` (str, required): Prompt message to display

**Returns**: None

**Side Effects**: Prints prompt to console (no trailing newline - allows inline input)

**Format**:
```
→ {prompt}
```

---

#### `clear_screen(self) -> None`

Clear console screen (platform-dependent implementation).

**Parameters**: None

**Returns**: None

**Side Effects**: Prints blank lines or platform-specific clear command

**Format**:
```
[prints 50 blank lines or uses os.system('cls'/'clear')]
```

---

## Status Indicators

### Completion Status

| Status Value | Display Text | Indicator |
|--------------|---------------|------------|
| False | ⏳ Pending | ⏳ |
| True | ✓ Completed | ✓ |

### Priority Indicators (Future Use - Not Phase I)

| Priority | Display Text | Indicator |
|----------|---------------|------------|
| low | Low | 🟢 |
| medium | Medium | 🟡 |
| high | High | 🔴 |

---

## Formatting Principles

### Visual Separation

- Use horizontal lines (─) for section headers
- Use box drawing (═) for main menu title
- Blank lines between major sections

### Consistency

- All menus use numbered list (1., 2., 3., ...)
- All messages use same indicator style (✓, ✗, →)
- Status always displayed with same indicators

### Readability

- Left-align task IDs with padding
- Clear column alignment for task attributes
- Avoid line wrapping for task titles (Phase I: no length limits)

### User-Friendly

- Non-technical error messages
- Clear action indicators (what succeeded vs failed)
- Minimal visual noise (no unnecessary decoration)

---

## Example Outputs

### Main Menu

```
═════════════════════════════════
 TODO LIST MANAGER
═════════════════════════════════

1. Add Task
2. Update Task
3. Delete Task
4. List Tasks
5. Mark Task as Complete
6. Exit

Enter your choice (1-6):
```

### Task List (2 Tasks)

```
─────────────────────────────────────────
 YOUR TASKS
─────────────────────────────────────────

Task ID 1: Buy groceries
  Status: ✓ Completed

Task ID 2: Write report
  Status: ⏳ Pending

─────────────────────────────────────────
Total: 2 tasks
```

### Success Message

```
✓ Success: Task created successfully
  Task ID: 3
```

### Error Message

```
✗ Error: Task not found
  Task ID: 999
  Please check the ID and try again.
```

### Input Prompt

```
→ Task title: Buy groceries
→ Task description (optional): Milk, eggs, bread
```

---

## Performance

- All display methods are O(1) (no loops)
- Task list display: O(n) where n = number of tasks
- No expensive string formatting operations
- Minimal string allocations in hot paths

## Platform Considerations

### Cross-Platform

- Uses standard print() for all output
- No ANSI color codes (Phase I constraint: plain text only)
- Unicode characters (✓, ✗, ⏳) widely supported

### Screen Clearing

- Optional functionality (not required)
- Implementation detail: Use 50 blank lines or platform-specific commands
- Graceful degradation: If clear fails, continue with output

## Design Principles

1. **Clarity**: Output should be immediately understandable
2. **Consistency**: Use same formatting across all displays
3. **Conciseness**: Avoid unnecessary verbosity
4. **Hierarchy**: Use visual indicators to show importance (✓, ✗, →)
5. **Actionability**: Make next steps clear (prompts, menu choices)
