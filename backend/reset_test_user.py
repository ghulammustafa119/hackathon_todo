#!/usr/bin/env python3
"""
Script to reset and add a test user to the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select, delete
from src.database import engine
from src.models.user import User

def reset_and_create_test_user():
    """Reset and create a test user in the database"""
    with Session(engine) as session:
        # Delete existing test user
        stmt = delete(User).where(User.email == "test@example.com")
        result = session.exec(stmt)
        session.commit()
        print(f"Deleted {result.rowcount} existing test user(s)")

        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Hash the password
        hashed_password = pwd_context.hash("Password123")

        # Create new test user
        test_user = User(
            email="test@example.com",
            password=hashed_password,
            name="Test User"
        )

        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        print(f"Test user created successfully! ID: {test_user.id}")
        print("Email: test@example.com")
        print("Password: Password123")

if __name__ == "__main__":
    reset_and_create_test_user()