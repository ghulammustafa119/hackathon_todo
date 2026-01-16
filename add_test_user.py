#!/usr/bin/env python3
"""
Script to add a test user to the database for authentication testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from sqlmodel import Session, select
from src.database import engine
from src.models.user import User
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a test user in the database"""
    with Session(engine) as session:
        # Check if test user already exists
        existing_user = session.exec(select(User).where(User.email == "test@example.com")).first()

        if existing_user:
            print("Test user already exists!")
            return

        # Hash the password
        hashed_password = pwd_context.hash("password123")

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
        print("Password: password123")

if __name__ == "__main__":
    create_test_user()