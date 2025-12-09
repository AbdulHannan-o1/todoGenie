from dataclasses import dataclass

@dataclass
class Task:
    """Represents a single to-do item."""
    id: int
    description: str
    status: str = "pending"
