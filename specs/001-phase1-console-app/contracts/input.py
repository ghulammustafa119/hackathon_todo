# Input Validation Contract

## Purpose

Validates user input for menu choices, task IDs, and task fields.

## Class: InputValidator

Provides validation methods for all user-facing input in console application.

### Methods

#### `validate_task_id(self, task_id: str) -> Optional[int]`

Validate and parse task ID from user input string.

**Parameters**:
- `task_id` (str, required): Raw user input for task ID

**Returns**: Optional[int] - Integer ID if valid, None if invalid

**Side Effects**: None

**Validation Rules**:
- Input must be numeric (digits only)
- Parsed integer must be positive (>0)
- Returns integer value or None

---

#### `validate_title(self, title: str) -> bool`

Validate task title for non-empty and non-whitespace.

**Parameters**:
- `title` (str, required): Raw user input for task title

**Returns**: bool - True if valid, False if invalid

**Side Effects**: None

**Validation Rules**:
- After stripping whitespace: length must be >0
- Empty string after stripping: invalid

---

#### `validate_menu_choice(self, choice: str, valid_range: Tuple[int, int]) -> bool`

Validate menu selection against valid range of options.

**Parameters**:
- `choice` (str, required): Raw user input for menu selection
- `valid_range` (tuple[int, int], required): Tuple of (min, max) inclusive range

**Returns**: bool - True if choice is within valid_range, False otherwise

**Side Effects**: None

**Validation Rules**:
- Input must be numeric (digits only)
- Parsed integer must be >= min and <= max
- Returns boolean result

---

#### `validate_description(self, description: str) -> bool`

Validate task description (always optional).

**Parameters**:
- `description` (str, required): Raw user input for task description

**Returns**: bool - Always returns True

**Side Effects**: None

**Validation Rules**:
- Description is optional, any string value is valid
- No length limits for Phase I

---

#### `get_validated_input(self, prompt: str, validator: Callable[[str], Any]) -> Any`

Generic method to collect and validate user input with retries.

**Parameters**:
- `prompt` (str, required): Message to display to user
- `validator` (callable, required): Function that takes str input and returns validated value or raises ValueError

**Returns**: Any - Validated value from validator

**Side Effects**:
- Displays prompt to console
- Reads user input from stdin
- Calls validator with input
- Loops on ValueError until valid input or user cancels

**Behavior**:
- Infinite retry loop with validation
- Allows user to cancel (empty input)
- Returns None on cancellation

## Error Messages

Pre-defined user-friendly error messages for validation failures:

### Task ID Validation

- Non-numeric: "Please enter a valid numeric task ID"
- Not found (via storage): "Task not found. Please check the ID and try again"

### Title Validation

- Empty: "Task title cannot be empty. Please enter a title."

### Menu Choice Validation

- Invalid: "Invalid choice. Please select a number between {min} and {max}"

## Usage Examples

### Validate Task ID

```python
validator = InputValidator()

user_input = "123"
task_id = validator.validate_task_id(user_input)
# Returns: 123

user_input = "abc"
task_id = validator.validate_task_id(user_input)
# Returns: None

user_input = "-5"
task_id = validator.validate_task_id(user_input)
# Returns: None (not positive)
```

### Validate Title

```python
validator = InputValidator()

title = "Buy groceries"
is_valid = validator.validate_title(title)
# Returns: True

title = "   "
is_valid = validator.validate_title(title)
# Returns: False (whitespace only)
```

### Validate Menu Choice

```python
validator = InputValidator()

choice = "3"
is_valid = validator.validate_menu_choice(choice, (1, 6))
# Returns: True

choice = "7"
is_valid = validator.validate_menu_choice(choice, (1, 6))
# Returns: False (out of range)
```

### Collect Validated Input

```python
validator = InputValidator()

def validate_title_input(input_str: str) -> str:
    if not validator.validate_title(input_str):
        raise ValueError("Title cannot be empty")
    return input_str.strip()

title = validator.get_validated_input("Enter task title: ", validate_title_input)
# Displays prompt, reads input, validates, retries on error
```

## Design Principles

- **Fail Fast**: Validation fails immediately on invalid input
- **Clear Messages**: User-friendly error messages without technical jargon
- **Type Safety**: Returns Optional[int] for nullable values
- **No Side Effects**: Validation methods are pure functions (no I/O)
- **Composable**: Can be used independently or with generic input collection
