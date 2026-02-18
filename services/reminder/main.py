"""Reminder Service - Consumes task events and schedules reminders via Dapr."""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reminder-service")

app = FastAPI(title="Reminder Service")

DAPR_HTTP_PORT = 3500
DAPR_STATE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore"
DAPR_PUBLISH_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/taskevents/notifications"


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "reminder"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "taskevents",
            "topic": "tasks",
            "route": "/events/tasks",
        }
    ]


@app.post("/events/tasks")
async def handle_task_event(event: dict):
    """Process task events to schedule/cancel reminders."""
    try:
        data = event.get("data", {})
        event_type = data.get("event_type", "")
        task_id = data.get("task_id", "")
        user_id = data.get("user_id", "")
        payload = data.get("payload", {})

        logger.info(f"Received event: {event_type} for task {task_id}")

        if event_type == "task.created" and payload.get("due_date"):
            await schedule_reminder(task_id, user_id, payload)
        elif event_type == "task.updated" and payload.get("due_date"):
            await cancel_reminder(task_id)
            await schedule_reminder(task_id, user_id, payload)
        elif event_type in ("task.deleted", "task.completed"):
            await cancel_reminder(task_id)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {"status": "RETRY"}


async def schedule_reminder(task_id: str, user_id: str, payload: dict):
    """Schedule a reminder based on due_date and reminder_lead_time."""
    due_date_str = payload.get("due_date")
    lead_time_minutes = payload.get("reminder_lead_time", 60)

    if not due_date_str:
        return

    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
    from datetime import timedelta
    remind_at = due_date - timedelta(minutes=lead_time_minutes)

    reminder_data = {
        "task_id": task_id,
        "user_id": user_id,
        "task_title": payload.get("title", ""),
        "due_date": due_date_str,
        "remind_at": remind_at.isoformat(),
        "status": "pending",
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            DAPR_STATE_URL,
            json=[{"key": f"reminder-{task_id}", "value": reminder_data}],
        )
    logger.info(f"Scheduled reminder for task {task_id} at {remind_at}")


async def cancel_reminder(task_id: str):
    """Cancel a scheduled reminder."""
    async with httpx.AsyncClient() as client:
        await client.delete(f"{DAPR_STATE_URL}/reminder-{task_id}")
    logger.info(f"Cancelled reminder for task {task_id}")


async def check_pending_reminders():
    """Background loop to check for due reminders every 30 seconds."""
    while True:
        try:
            now = datetime.now(timezone.utc)
            # Note: In production, this would query all pending reminders
            # For now, this is a placeholder for the scheduler loop
            logger.debug(f"Checking reminders at {now}")
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
        await asyncio.sleep(30)


@app.on_event("startup")
async def startup():
    asyncio.create_task(check_pending_reminders())
    logger.info("Reminder service started")
