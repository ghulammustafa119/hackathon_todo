#!/usr/bin/env python3
"""
Database initialization script
"""

from sqlmodel import SQLModel
from sqlalchemy import text
from src.database.session import engine
from src.models.user import User
from src.models.task import Task
from src.models.conversation import ConversationMessage, ConversationHistory
from src.models.event import TaskEvent, OutboxEvent
from src.models.tag import Tag, TaskTag
from src.models.audit import AuditEntry
from src.models.reminder import ReminderSchedule


def migrate_task_table():
    """Add missing Phase V columns to existing task table."""
    columns = [
        ("priority", "VARCHAR DEFAULT 'medium'"),
        ("due_date", "TIMESTAMP"),
        ("reminder_lead_time", "INTEGER DEFAULT 60"),
        ("recurrence_rule", "VARCHAR"),
        ("recurrence_parent_id", "VARCHAR"),
        ("completed_at", "TIMESTAMP"),
    ]
    migrations = {
        "task": columns,
        "conversationhistory": [
            ("message_count", "INTEGER DEFAULT 0"),
            ("timeout_minutes", "INTEGER DEFAULT 30"),
        ],
        "conversationmessage": [
            ("task_references", "TEXT"),
            ("token_count", "INTEGER"),
            ("tool_calls", "TEXT"),
        ],
    }
    with engine.connect() as conn:
        for table, cols in migrations.items():
            for col_name, col_type in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"  Ensured column: {table}.{col_name}")
        conn.commit()


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

    print("Running migrations...")
    migrate_task_table()

    print("Database initialized with all Phase V tables.")


if __name__ == "__main__":
    create_tables()
