"""Input validation service for Phase I console app
Contract: specs/001-phase1-console-app/contracts/input.py
"""


from typing import Callable, Any


class InputValidator:
    """Validates user input for menu choices, task IDs, and task fields"""

    def validate_task_id(self, task_id: str) -> int | None:
        """
        Validate and parse task ID from user input string

        Args:
            task_id: Raw user input for task ID

        Returns:
            int | None: Integer ID if valid, None if invalid
        """
        if not task_id or not task_id.isdigit():
            return None
        task_id_int = int(task_id)
        return task_id_int if task_id_int > 0 else None

    def validate_title(self, title: str) -> bool:
        """
        Validate task title for non-empty and non-whitespace

        Args:
            title: Raw user input for task title

        Returns:
            bool: True if valid, False if invalid
        """
        return bool(title.strip())

    def validate_menu_choice(self, choice: str, valid_range: tuple[int, int]) -> bool:
        """
        Validate menu selection against valid range of options

        Args:
            choice: Raw user input for menu selection
            valid_range: Tuple of (min, max) inclusive range

        Returns:
            bool: True if choice is within valid_range, False otherwise
        """
        if not choice.isdigit():
            return False
        choice_int = int(choice)
        min_val, max_val = valid_range
        return min_val <= choice_int <= max_val

    def validate_description(self, description: str) -> bool:
        """
        Validate task description (always optional)

        Args:
            description: Raw user input for task description

        Returns:
            bool: Always returns True (description is optional)
        """
        return True

    def get_validated_input(self, prompt: str, validator: Callable[[str], Any]) -> Any:
        """
        Generic method to collect and validate user input with retries

        Args:
            prompt: Message to display to user
            validator: Function that takes str input and returns validated value or raises ValueError

        Returns:
            Any: Validated value from validator

        Side Effects:
            - Displays prompt to console
            - Reads user input from stdin
            - Calls validator with input
            - Loops on ValueError until valid input or user cancels

        Behavior:
            - Infinite retry loop with validation
            - Allows user to cancel (empty input)
            - Returns None on cancellation
        """
        while True:
            print(f"→ {prompt}")
            user_input = input().strip()

            if not user_input:  # User cancelled
                return None

            try:
                validated = validator(user_input)
                return validated
            except ValueError as e:
                print(f"✗ {e}")
