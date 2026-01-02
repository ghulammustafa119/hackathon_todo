"""Console output rendering for Phase I console app
Contract: specs/001-phase1-console-app/contracts/render.py
"""


class ConsoleRenderer:
    """Formats and displays user-facing output"""

    @staticmethod
    def display_menu(title: str, options: list[str]):
        """Display main menu with title and numbered options"""
        print("═" * 40)
        print(f" {title}")
        print("═" * 40)
        print()
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print(f"\nEnter your choice (1-{len(options)}): ")

    @staticmethod
    def display_task_list(tasks: list):
        """Display all tasks in readable format with ID, title, and completion status"""
        print("─" * 40)
        print(" YOUR TASKS")
        print("─" * 40)
        print()
        if not tasks:
            print("No tasks found. Create your first task!")
        else:
            for task in tasks:
                status = "✓ Completed" if task.completed else "⏳ Pending"
                print(f"Task ID {task.id}: {task.title}")
                print(f"  Status: {status}")
                print()
        print("─" * 40)
        print(f"Total: {len(tasks)} tasks")

    @staticmethod
    def display_success(message: str):
        """Display success message for completed operations"""
        print(f"✓ Success: {message}")

    @staticmethod
    def display_error(message: str):
        """Display error message for failed operations"""
        print(f"✗ Error: {message}")
    @staticmethod
    def display_prompt(prompt: str):
        """Display input prompt for user data collection"""
        print(f"→ {prompt}")
