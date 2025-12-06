from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from typing import List
from spec import Task

console = Console()

def display_tasks(tasks: List[Task]):
    """Displays a list of tasks in a table."""
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Status", style="green")

    for task in tasks:
        table.add_row(str(task.id), task.description, task.status)

    console.print(table)

def confirm_delete(task_id: int) -> bool:
    """Asks for user confirmation before deleting a task."""
    return Confirm.ask(f"Are you sure you want to delete task {task_id}?")
