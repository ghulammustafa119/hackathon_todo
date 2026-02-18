"""Recurrence Service - Creates new task instances when recurring tasks are completed."""

import logging
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recurrence-service")

app = FastAPI(title="Recurrence Service")

DAPR_HTTP_PORT = 3500
DAPR_PUBLISH_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/taskevents/task-commands"
DAPR_STATE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore"


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "recurrence"}


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
    """Process task.completed events for recurring tasks."""
    try:
        data = event.get("data", {})
        event_type = data.get("event_type", "")
        payload = data.get("payload", {})

        if event_type != "task.completed":
            return {"status": "SUCCESS"}

        recurrence_rule = payload.get("recurrence_rule")
        if not recurrence_rule:
            return {"status": "SUCCESS"}

        task_id = data.get("task_id", "")
        user_id = data.get("user_id", "")
        logger.info(f"Recurring task completed: {task_id}, rule: {recurrence_rule}")

        next_due = calculate_next_due_date(
            payload.get("due_date"),
            recurrence_rule,
        )

        command_event = {
            "command_type": "task.create.requested",
            "source_service": "recurrence-service",
            "task_data": {
                "title": payload.get("title", ""),
                "description": payload.get("description"),
                "priority": payload.get("priority", "medium"),
                "tags": payload.get("tags", []),
                "due_date": next_due.isoformat() if next_due else None,
                "reminder_lead_time": payload.get("reminder_lead_time", 60),
                "recurrence_rule": recurrence_rule,
                "recurrence_parent_id": payload.get("recurrence_parent_id") or task_id,
                "user_id": user_id,
            },
        }

        async with httpx.AsyncClient() as client:
            await client.post(DAPR_PUBLISH_URL, json=command_event)

        logger.info(f"Published recurrence command for task {task_id}, next due: {next_due}")
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error processing recurrence: {e}")
        return {"status": "RETRY"}


def calculate_next_due_date(current_due_str: str | None, rule: str) -> datetime | None:
    """Calculate the next due date based on recurrence rule."""
    if not current_due_str:
        base = datetime.now(timezone.utc)
    else:
        base = datetime.fromisoformat(current_due_str.replace("Z", "+00:00"))

    rule_lower = rule.lower().strip()

    if rule_lower == "daily":
        return base + timedelta(days=1)
    elif rule_lower == "weekly":
        return base + timedelta(weeks=1)
    elif rule_lower == "monthly":
        month = base.month + 1
        year = base.year
        if month > 12:
            month = 1
            year += 1
        return base.replace(year=year, month=month)
    else:
        # Try cron expression
        try:
            from croniter import croniter
            cron = croniter(rule, base)
            return cron.get_next(datetime)
        except Exception:
            logger.warning(f"Invalid recurrence rule: {rule}")
            return base + timedelta(days=1)
