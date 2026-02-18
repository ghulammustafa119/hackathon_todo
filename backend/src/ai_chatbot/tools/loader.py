"""Module to ensure all tools are loaded and registered."""

# Import all tool modules to ensure they register themselves
from . import create_task_tool
from . import list_tasks_tool
from . import update_task_tool
from . import delete_task_tool
from . import complete_task_tool
from . import search_tasks_tool
from . import set_priority_tool
from . import add_tags_tool
from . import set_due_date_tool

def ensure_tools_loaded():
    """Function to ensure all tools are loaded."""
    # This function doesn't need to do anything - just importing the modules
    # ensures that the tools get registered in the global registry
    pass
