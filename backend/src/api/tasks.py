from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.models.user import User
from src.database import get_session
from src.api.deps import get_current_user
from src.services.task_service import TaskService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_user_id(user_id: str, current_user: dict):
    """Verify that the JWT user matches the URL user_id."""
    jwt_user_id = current_user.get("sub")
    if str(jwt_user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )
    return jwt_user_id


@router.post("/{user_id}/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    # Use the service layer to handle the creation with proper timezone handling
    task_service = TaskService(session)
    created_task = task_service.create_task(task, user_id)

    return created_task

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve all tasks for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    # Query tasks for the current user only
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

    return tasks

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def read_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    # Use the service layer to handle the update with proper timezone handling
    task_service = TaskService(session)
    updated_task = task_service.update_task(task_id, task_update, user_id)

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task

@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(db_task)
    session.commit()

    return {"message": "Task deleted successfully"}

@router.patch("/{user_id}/tasks/{task_id}/complete")
def toggle_task_completion(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task for the authenticated user.
    """
    _verify_user_id(user_id, current_user)

    # Use the service layer to handle the toggle with proper timezone handling
    task_service = TaskService(session)
    toggled_task = task_service.toggle_task_completion(task_id, user_id)

    if not toggled_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"id": toggled_task.id, "completed": toggled_task.completed}
