"""Audit Service - Captures all task events into an immutable audit log."""

import os
import logging
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select, col

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit-service")

app = FastAPI(title="Audit Service")

# Database for audit entries (uses same Neon PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audit.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


class AuditEntryDB(SQLModel, table=True):
    """Immutable audit log entry for task operations."""
    __tablename__ = "audit_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, index=True)
    event_type: str = Field(index=True)
    task_id: str = Field(index=True)
    user_id: str = Field(index=True)
    operation: str = Field(index=True)
    payload: str = Field()
    previous_state: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audit"}


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
    """Process task events and write to audit log with idempotency."""
    try:
        data = event.get("data", {})
        event_id = data.get("id", data.get("event_id", ""))
        event_type = data.get("event_type", data.get("type", ""))
        task_id = data.get("task_id", "")
        user_id = data.get("user_id", "")
        payload = data.get("data", data.get("payload", {}))
        previous_state = data.get("previous_state")

        if not event_id:
            logger.warning("Received event without ID, skipping")
            return {"status": "DROP"}

        # Idempotency check
        with Session(engine) as session:
            existing = session.exec(
                select(AuditEntryDB).where(AuditEntryDB.event_id == event_id)
            ).first()
            if existing:
                logger.info(f"Duplicate event {event_id}, skipping")
                return {"status": "SUCCESS"}

            operation = event_type.split(".")[-1] if "." in event_type else event_type

            entry = AuditEntryDB(
                event_id=event_id,
                event_type=event_type,
                task_id=task_id,
                user_id=user_id,
                operation=operation,
                payload=json.dumps(payload) if isinstance(payload, dict) else str(payload),
                previous_state=json.dumps(previous_state) if previous_state else None,
            )
            session.add(entry)
            session.commit()

        logger.info(f"Audit entry created for event {event_id}: {event_type}")
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Failed to process audit event: {e}")
        return {"status": "RETRY"}


@app.get("/api/admin/audit")
async def get_audit_log(
    user_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    operation: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Query audit log entries with optional filters."""
    with Session(engine) as session:
        statement = select(AuditEntryDB)

        if user_id:
            statement = statement.where(AuditEntryDB.user_id == user_id)
        if task_id:
            statement = statement.where(AuditEntryDB.task_id == task_id)
        if operation:
            statement = statement.where(AuditEntryDB.operation == operation)

        statement = statement.order_by(col(AuditEntryDB.timestamp).desc()).limit(limit)
        entries = session.exec(statement).all()

    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "task_id": e.task_id,
            "user_id": e.user_id,
            "operation": e.operation,
            "payload": e.payload,
            "previous_state": e.previous_state,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in entries
    ]
