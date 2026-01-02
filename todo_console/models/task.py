"""Task data model for Phase I console todo app
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a todo item in memory"""
    id: int
    title: str
    description: str | None = None
    completed: bool = False
