from enum import Enum
from typing import Optional

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    NONE = "None" # Explicitly handle no priority

class Task:
    def __init__(self, id: int, title: str, description: str, priority: Optional[Priority] = None, status: str = "pending"):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority if priority is not None else Priority.NONE
        self.status = status # Add status attribute

    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}', description='{self.description}', priority='{self.priority.value}', status='{self.status}')"

# src/models.py
# Defines the Task model
