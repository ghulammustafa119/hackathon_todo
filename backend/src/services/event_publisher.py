"""Event publisher service for Dapr pub/sub integration with CloudEvents and retry."""

import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlmodel import Session, select

from backend.src.models.event import OutboxEvent

logger = logging.getLogger("event-publisher")

DAPR_HTTP_PORT = 3500
DAPR_PUBLISH_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/taskevents/tasks"
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds


async def publish_outbox_events(session: Session):
    """Process unpublished outbox events with retry and exponential backoff."""
    unpublished = session.exec(
        select(OutboxEvent)
        .where(OutboxEvent.published_at == None)  # noqa: E711
        .order_by(OutboxEvent.created_at)
    ).all()

    for event in unpublished:
        success = await _publish_with_retry(event)
        if success:
            event.published_at = datetime.now(timezone.utc)
            session.add(event)
            session.commit()
        else:
            event.retry_count += 1
            session.add(event)
            session.commit()


async def _publish_with_retry(event: OutboxEvent) -> bool:
    """Attempt to publish an event via Dapr with exponential backoff."""
    payload = json.loads(event.payload)

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    DAPR_PUBLISH_URL,
                    json=payload,
                    headers={"Content-Type": "application/cloudevents+json"},
                )
                if resp.status_code < 300:
                    logger.info(f"Published outbox event {event.id} (attempt {attempt + 1})")
                    return True
                else:
                    logger.warning(f"Dapr returned {resp.status_code} for event {event.id}")
        except Exception as e:
            logger.warning(f"Publish attempt {attempt + 1} failed for event {event.id}: {e}")

        if attempt < MAX_RETRIES - 1:
            delay = BASE_DELAY * (2 ** attempt)
            await asyncio.sleep(delay)

    logger.error(f"Failed to publish event {event.id} after {MAX_RETRIES} attempts")
    return False
