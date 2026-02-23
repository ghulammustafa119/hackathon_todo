from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, col
from typing import List, Optional
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.models.event import TaskEvent
from src.models.user import User
from src.database import get_session
from src.api.deps import get_current_user
from src.services.task_service import TaskService
from pydantic import BaseModel
import json
import logging

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
    """Create a new task for the authenticated user."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)
    created_task = task_service.create_task(task, user_id)

    # Attach tags to response
    tags = task_service.get_task_tags(created_task.id)
    response = TaskRead.model_validate(created_task)
    response.tags = tags
    return response


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str,
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="asc or desc"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    task_status: Optional[str] = Query(None, alias="status", description="completed or pending"),
    search: Optional[str] = Query(None, description="Search title and description"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retrieve tasks with optional filtering, sorting, and search."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)

    tasks = task_service.get_tasks_by_user(
        user_id,
        sort_by=sort_by,
        sort_order=sort_order,
        priority=priority,
        tag=tag,
        status=task_status,
        search=search,
    )

    result = []
    for t in tasks:
        tr = TaskRead.model_validate(t)
        tr.tags = task_service.get_task_tags(t.id)
        result.append(tr)
    return result


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def read_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retrieve a specific task by ID for the authenticated user."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)

    task = task_service.get_task_by_id(task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    response = TaskRead.model_validate(task)
    response.tags = task_service.get_task_tags(task.id)
    return response


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific task by ID for the authenticated user."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)
    updated_task = task_service.update_task(task_id, task_update, user_id)

    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    response = TaskRead.model_validate(updated_task)
    response.tags = task_service.get_task_tags(updated_task.id)
    return response


@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific task by ID for the authenticated user."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)
    deleted = task_service.delete_task(task_id, user_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {"message": "Task deleted successfully"}


@router.patch("/{user_id}/tasks/{task_id}/complete")
def toggle_task_completion(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle the completion status of a specific task for the authenticated user."""
    _verify_user_id(user_id, current_user)
    task_service = TaskService(session)
    toggled_task = task_service.toggle_task_completion(task_id, user_id)

    if not toggled_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {"id": toggled_task.id, "completed": toggled_task.completed}


class AuditEventResponse(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    changes: Optional[dict] = None


@router.get("/{user_id}/tasks/{task_id}/events", response_model=List[AuditEventResponse])
def get_task_events(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get audit log (event history) for a specific task."""
    _verify_user_id(user_id, current_user)

    events = session.exec(
        select(TaskEvent)
        .where(TaskEvent.task_id == task_id, TaskEvent.user_id == user_id)
        .order_by(col(TaskEvent.timestamp).desc())
    ).all()

    result = []
    for ev in events:
        changes = None
        if ev.event_type == "task.updated" and ev.previous_state:
            try:
                prev = json.loads(ev.previous_state)
                curr = json.loads(ev.payload)
                changes = {}
                for key in ("title", "description", "priority", "due_date", "completed"):
                    old_val = prev.get(key)
                    new_val = curr.get(key)
                    if old_val != new_val:
                        changes[key] = {"from": old_val, "to": new_val}
            except (json.JSONDecodeError, TypeError):
                pass

        result.append(AuditEventResponse(
            event_id=ev.event_id,
            event_type=ev.event_type,
            timestamp=ev.timestamp.isoformat(),
            changes=changes,
        ))

    return result
