"""MCP Server for Todo Task Operations."""

from typing import Dict, Any, Optional
from mcp.server import FastMCP
from mcp import Tool
from pydantic import BaseModel, Field
from datetime import datetime
from contextlib import contextmanager
from sqlmodel import Session, select
from ..models.task import Task
from ..database.session import get_session


# Create an MCP server for todo operations
mcp = FastMCP("TodoMCP")


class CreateTaskParams(BaseModel):
    """Parameters for create_task tool."""
    token: str
    title: str
    description: Optional[str] = ""


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    token: str
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""
    token: str
    task_id: str


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool."""
    token: str
    task_id: str
    completed: bool = True


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    token: str
    filter_status: Optional[str] = "all"


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = next(get_session())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return user info.
    Delegates to the central verify_token in deps.py which supports
    both Better Auth JWKS (EdDSA) and HS256 fallback.

    Args:
        token: JWT token to verify

    Returns:
        User information dictionary
    """
    # Handle case where token might be prefixed with "Bearer "
    if token.startswith("Bearer "):
        token = token[7:]

    token = token.strip()

    if not token:
        raise ValueError("Token is empty")

    try:
        from ..api.deps import verify_token as deps_verify_token
        return deps_verify_token(token)
    except Exception as e:
        # deps.verify_token raises HTTPException on failure;
        # convert to ValueError for MCP tool error handling
        detail = getattr(e, 'detail', str(e))
        raise ValueError(f"Invalid token: {detail}")


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert a Task model to a dictionary for API responses."""
    return {
        "id": str(task.id),
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@mcp.tool(
    "create_task",
    "Create a new task with title and optional description via MCP server"
)
def create_task(params: CreateTaskParams) -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        params: Parameters including token, title, and description

    Returns:
        Dictionary containing created task details
    """
    try:
        # Verify the token and get user info
        user_info = verify_token(params.token)
        user_id = user_info.get("sub")

        if not user_id:
            return {
                "success": False,
                "error": "Invalid token: no user ID found"
            }

        # Create the task in the database
        with get_db_session() as session:
            task = Task(
                user_id=user_id,
                title=params.title,
                description=params.description if params.description else None,
                completed=False
            )

            session.add(task)
            session.flush()  # Get the ID without committing

            return {
                "success": True,
                "task": _task_to_dict(task),
                "message": f"Task '{params.title}' created successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


@mcp.tool(
    "list_tasks",
    "Retrieve tasks via MCP server"
)
def list_tasks(params: ListTasksParams) -> Dict[str, Any]:
    """
    List all tasks for the user.

    Args:
        params: Parameters including token and filter status

    Returns:
        Dictionary containing list of tasks
    """
    try:
        # Verify the token and get user info
        user_info = verify_token(params.token)
        user_id = user_info.get("sub")

        if not user_id:
            return {
                "success": False,
                "error": "Invalid token: no user ID found"
            }

        # Query tasks from the database
        with get_db_session() as session:
            query = select(Task).where(Task.user_id == user_id)

            # Apply filter if specified
            if params.filter_status == "pending":
                query = query.where(Task.completed == False)
            elif params.filter_status == "completed":
                query = query.where(Task.completed == True)

            tasks = session.exec(query).all()

            task_dicts = [_task_to_dict(task) for task in tasks]

            return {
                "success": True,
                "tasks": task_dicts,
                "count": len(task_dicts)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }


@mcp.tool(
    "update_task",
    "Update an existing task with new values via MCP server"
)
def update_task(params: UpdateTaskParams) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        params: Parameters including token, task_id, and optional fields to update

    Returns:
        Dictionary containing updated task details
    """
    try:
        # Verify the token and get user info
        user_info = verify_token(params.token)
        user_id = user_info.get("sub")

        if not user_id:
            return {
                "success": False,
                "error": "Invalid token: no user ID found"
            }

        # Update the task in the database
        with get_db_session() as session:
            # Find the task
            task = session.exec(select(Task).where(Task.id == str(params.task_id), Task.user_id == user_id)).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task with ID {params.task_id} not found or does not belong to user"
                }

            # Update fields if provided
            if params.title is not None:
                task.title = params.title
            if params.description is not None:
                task.description = params.description

            task.updated_at = datetime.now()
            session.add(task)

            return {
                "success": True,
                "task": _task_to_dict(task),
                "message": f"Task '{params.task_id}' updated successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }


@mcp.tool(
    "delete_task",
    "Delete a task via MCP server"
)
def delete_task(params: DeleteTaskParams) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        params: Parameters including token and task_id

    Returns:
        Dictionary containing deletion confirmation
    """
    try:
        # Verify the token and get user info
        user_info = verify_token(params.token)
        user_id = user_info.get("sub")

        if not user_id:
            return {
                "success": False,
                "error": "Invalid token: no user ID found"
            }

        # Delete the task from the database
        with get_db_session() as session:
            # Find the task
            task = session.exec(select(Task).where(Task.id == str(params.task_id), Task.user_id == user_id)).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task with ID {params.task_id} not found or does not belong to user"
                }

            session.delete(task)

            return {
                "success": True,
                "task_id": params.task_id,
                "message": f"Task '{params.task_id}' deleted successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }


@mcp.tool(
    "complete_task",
    "Toggle the completion status of a task via MCP server"
)
def complete_task(params: CompleteTaskParams) -> Dict[str, Any]:
    """
    Mark a task as complete or incomplete.

    Args:
        params: Parameters including token, task_id, and completion status

    Returns:
        Dictionary containing updated task details
    """
    try:
        # Verify the token and get user info
        user_info = verify_token(params.token)
        user_id = user_info.get("sub")

        if not user_id:
            return {
                "success": False,
                "error": "Invalid token: no user ID found"
            }

        # Update task completion status in the database
        with get_db_session() as session:
            # Find the task
            task = session.exec(select(Task).where(Task.id == str(params.task_id), Task.user_id == user_id)).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task with ID {params.task_id} not found or does not belong to user"
                }

            task.completed = params.completed
            task.completed_at = datetime.now() if params.completed else None
            task.updated_at = datetime.now()
            session.add(task)

            status = "completed" if params.completed else "marked as incomplete"
            return {
                "success": True,
                "task": _task_to_dict(task),
                "message": f"Task '{params.task_id}' {status} successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task completion: {str(e)}"
        }


# Run with streamable HTTP transport for integration with AI agents
if __name__ == "__main__":
    import uvicorn
    from mcp.server.sse import create_sse_transport
    app = mcp.to_asgi_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
