from sqlmodel import create_engine, Session
from typing import Generator
import os
import re

# Get database URL from environment, with a default for development
# Collapse any whitespace inside the URL (HF Spaces secrets can add stray spaces)
DATABASE_URL = re.sub(r'\s+', '', os.getenv("DATABASE_URL", "sqlite:///./todo_app.db"))

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session