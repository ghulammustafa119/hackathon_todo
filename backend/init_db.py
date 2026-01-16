#!/usr/bin/env python3
"""
Database initialization script
"""

from sqlmodel import SQLModel
from src.database import engine
from src.models.user import User
from src.models.task import Task

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")
    print("Database initialized with User and Task tables.")

if __name__ == "__main__":
    create_tables()