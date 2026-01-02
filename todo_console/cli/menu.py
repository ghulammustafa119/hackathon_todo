"""Menu display and navigation for Phase I console app
Contract: specs/001-phase1-console-app/contracts/render.py (partial)
"""


class MainMenu:
    """Main menu for Phase I console todo app"""

    MENU_OPTIONS = [
        "Add Task",
        "Update Task",
        "Delete Task",
        "List Tasks",
        "Mark Task as Complete",
        "Exit"
    ]

    def display(self):
        """Display main menu with title and numbered options"""
        print("═" * 40)
        print(" TODO LIST MANAGER")
        print("═" * 40)
        print()
        for i, option in enumerate(self.MENU_OPTIONS, 1):
            print(f"{i}. {option}")
        print(f"\nEnter your choice (1-{len(self.MENU_OPTIONS)}): ")

    def get_choice(self, min_choice: int = 1, max_choice: int = 6) -> int:
        """Collect and validate user's menu choice"""
        while True:
            choice_input = input().strip()

            if choice_input.isdigit():
                choice_int = int(choice_input)
                if min_choice <= choice_int <= max_choice:
                    return choice_int

            print(f"Invalid choice. Please select a number between {min_choice} and {max_choice}")

    def display_subtask_menu(self, task_id: int):
        """Display secondary menu for task operations"""
        print("\nTask ID:", task_id)
        print("1. Update Title")
        print("2. Update Description")
        print("3. Cancel")
        return

    def get_subtask_choice(self) -> int:
        """Collect and validate subtask choice"""
        while True:
            choice_input = input().strip()
            if choice_input.isdigit() and choice_input in ["1", "2", "3"]:
                return int(choice_input)
            print("Invalid choice. Please select 1, 2, or 3")
