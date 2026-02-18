"""Notifications API for in-app reminder alerts."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from typing import List
from pydantic import BaseModel
from src.database import get_session
from src.api.deps import get_current_user
from src.models.reminder import ReminderSchedule

router = APIRouter()


class NotificationResponse(BaseModel):
    id: str
    task_id: str
    remind_at: str
    status: str


@router.get("/{user_id}/notifications", response_model=List[NotificationResponse])
def get_notifications(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get pending/sent notifications for the user."""
    jwt_user_id = current_user.get("sub")
    if str(jwt_user_id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    reminders = session.exec(
        select(ReminderSchedule)
        .where(ReminderSchedule.user_id == user_id)
        .where(col(ReminderSchedule.status).in_(["pending", "sent"]))
        .order_by(col(ReminderSchedule.remind_at).desc())
    ).all()

    return [
        NotificationResponse(
            id=r.id,
            task_id=r.task_id,
            remind_at=r.remind_at.isoformat(),
            status=r.status,
        )
        for r in reminders
    ]


@router.patch("/{user_id}/notifications/{notification_id}/read")
def mark_notification_read(
    user_id: str,
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Mark a notification as read (cancelled)."""
    jwt_user_id = current_user.get("sub")
    if str(jwt_user_id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    reminder = session.exec(
        select(ReminderSchedule)
        .where(ReminderSchedule.id == notification_id, ReminderSchedule.user_id == user_id)
    ).first()

    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    reminder.status = "cancelled"
    session.add(reminder)
    session.commit()

    return {"message": "Notification marked as read"}
