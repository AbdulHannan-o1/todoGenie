import sys
from commands import add_task, list_tasks, update_task, complete_task, delete_task
from utils import console, display_tasks, confirm_delete

def display_help():
    """Displays the help message."""
    help_message = """
Usage: python app.py <command> [arguments]

Commands:
  add <description>         Add a new task.
  list                      List all tasks.
  update <id> <new-description> Update a task's description.
  complete <id>             Mark a task as complete.
  delete <id>               Delete a task.
  help                      Show this help message.
"""
    console.print(help_message)

def main():
    """Main entry point for the CLI application."""
    if len(sys.argv) < 2:
        display_help()
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            console.print("Usage: python app.py add <description>")
            return
        description = " ".join(sys.argv[2:])
        task = add_task(description)
        console.print(f"Added task: '{task.description}' with ID {task.id}")
    elif command == "list":
        tasks = list_tasks()
        display_tasks(tasks)
    elif command == "update":
        if len(sys.argv) < 4:
            console.print("Usage: python app.py update <id> <new-description>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            console.print("Error: Task ID must be an integer.")
            return
        new_description = " ".join(sys.argv[3:])
        task = update_task(task_id, new_description)
        if task:
            console.print(f"Updated task {task_id} to: '{task.description}'")
        else:
            console.print(f"Error: Task with ID {task_id} not found.")
    elif command == "complete":
        if len(sys.argv) < 3:
            console.print("Usage: python app.py complete <id>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            console.print("Error: Task ID must be an integer.")
            return
        task = complete_task(task_id)
        if task:
            console.print(f"Completed task {task_id}: '{task.description}'")
        else:
            console.print(f"Error: Task with ID {task_id} not found.")
    elif command == "delete":
        if len(sys.argv) < 3:
            console.print("Usage: python app.py delete <id>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            console.print("Error: Task ID must be an integer.")
            return
        if confirm_delete(task_id):
            if delete_task(task_id):
                console.print(f"Deleted task {task_id}.")
            else:
                console.print(f"Error: Task with ID {task_id} not found.")
        else:
            console.print(f"Deletion of task {task_id} cancelled.")
    elif command == "help":
        display_help()
    else:
        console.print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()