"""Tag management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from pydantic import BaseModel
from src.database import get_session
from src.api.deps import get_current_user
from src.services.task_service import TaskService

router = APIRouter()


class TagResponse(BaseModel):
    id: int
    name: str


class TagListResponse(BaseModel):
    tags: List[TagResponse]


@router.get("/{user_id}/tags", response_model=TagListResponse)
def get_user_tags(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all tags for the authenticated user."""
    jwt_user_id = current_user.get("sub")
    if str(jwt_user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    task_service = TaskService(session)
    tags = task_service.get_user_tags(user_id)
    return TagListResponse(tags=[TagResponse(id=t.id, name=t.name) for t in tags])
