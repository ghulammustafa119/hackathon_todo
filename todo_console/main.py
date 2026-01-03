"""
Phase I - In-Memory Console Todo App
Main application entry point
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todo_console.services.storage import TaskStorage
from todo_console.services.operations import TaskOperations
from todo_console.cli.menu import MainMenu
from todo_console.cli.render import ConsoleRenderer


def main():
    """Main application loop"""
    # Initialize components
    storage = TaskStorage()
    operations = TaskOperations(storage)
    renderer = ConsoleRenderer()
    menu = MainMenu()

    # Main application loop
    print("\nWelcome to Todo List Manager!")

    while True:
        # Display menu and get user choice
        menu.display()
        choice = menu.get_choice()

        # Process user choice
        if choice == 1:  # Add Task
            title = input("Task title: ").strip()
            if not title:
                renderer.display_error("Title cannot be empty")
                continue

            description = input("Task description (optional): ").strip()
            result = operations.create_task(title, description)
            if result["success"]:
                renderer.display_success(f"Task created with ID {result['task_id']}")
            else:
                renderer.display_error(result.get("error", "Task creation failed"))

        elif choice == 2:  # Update Task
            task_id_input = input("Task ID to update: ").strip()
            task_id = operations.validator.validate_task_id(task_id_input)
            if task_id is None:
                renderer.display_error("Invalid task ID")
                continue

            # Display subtask menu and get choice
            menu.display_subtask_menu(task_id)
            sub_choice = menu.get_subtask_choice()

            if sub_choice == 3:  # Cancel
                continue
            elif sub_choice == 1:  # Update Title
                new_title = input("New title: ").strip()
                result = operations.update_task(task_id, title=new_title)
                if result["success"]:
                    renderer.display_success(f"Task {task_id} updated")
                else:
                    renderer.display_error(result.get("error", "Update failed"))
            elif sub_choice == 2:  # Update Description
                new_description = input("New description: ").strip()
                result = operations.update_task(task_id, description=new_description)
                if result["success"]:
                    renderer.display_success(f"Task {task_id} updated")
                else:
                    renderer.display_error(result.get("error", "Update failed"))

        elif choice == 3:  # Delete Task
            task_id_input = input("Task ID to delete: ").strip()
            task_id = operations.validator.validate_task_id(task_id_input)
            if task_id is None:
                renderer.display_error("Invalid task ID")
                continue

            result = operations.delete_task(task_id)
            if result["success"]:
                renderer.display_success(f"Task {result['deleted_task_id']} deleted")
            else:
                renderer.display_error(result.get("error", "Deletion failed"))

        elif choice == 4:  # List Tasks
            result = operations.list_tasks()
            renderer.display_task_list(result["tasks"])

        elif choice == 5:  # Mark Task as Complete
            task_id_input = input("Task ID to toggle completion: ").strip()
            task_id = operations.validator.validate_task_id(task_id_input)
            if task_id is None:
                renderer.display_error("Invalid task ID")
                continue

            result = operations.toggle_completion(task_id)
            if result["success"]:
                old_status = "completed" if result["old_status"] else "not completed"
                new_status = "completed" if result["new_status"] else "not completed"
                renderer.display_success(f"Task {task_id} toggled: {old_status} → {new_status}")
            else:
                renderer.display_error(result.get("error", "Toggle failed"))

        elif choice == 6:  # Exit
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
