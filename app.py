import sys
from commands import add_task, list_tasks, update_task, complete_task, delete_task
from utils import console, display_tasks, confirm_delete
from rich.prompt import Prompt

def display_help():
    """Displays the help message."""
    help_message = """
Commands:
  add <description>         Add a new task.
  list                      List all tasks.
  update <id> <new-description> Update a task's description.
  complete <id>             Mark a task as complete.
  delete <id>               Delete a task.
  help                      Show this help message.
  exit                      Exit the application.
"""
    console.print(help_message)

def interactive_mode():
    """Runs the application in interactive mode."""
    while True:
        console.print("\n--- Current Tasks ---")
        tasks = list_tasks()
        display_tasks(tasks)
        console.print("---------------------\n")

        display_help()
        command_line = Prompt.ask("Enter command")
        args = command_line.split()

        if not args:
            continue

        command = args[0]

        if command == "add":
            if len(args) < 2:
                console.print("Usage: add <description>")
                continue
            description = " ".join(args[1:])
            task = add_task(description)
            console.print(f"Added task: '{task.description}' with ID {task.id}")
        elif command == "list":
            # Tasks are already displayed at the beginning of the loop
            pass
        elif command == "update":
            if len(args) < 3:
                console.print("Usage: update <id> <new-description>")
                continue
            try:
                task_id = int(args[1])
            except ValueError:
                console.print("Error: Task ID must be an integer.")
                continue
            new_description = " ".join(args[2:])
            task = update_task(task_id, new_description)
            if task:
                console.print(f"Updated task {task_id} to: '{task.description}'")
            else:
                console.print(f"Error: Task with ID {task_id} not found.")
        elif command == "complete":
            if len(args) < 2:
                console.print("Usage: complete <id>")
                continue
            try:
                task_id = int(args[1])
            except ValueError:
                console.print("Error: Task ID must be an integer.")
                continue
            task = complete_task(task_id)
            if task:
                console.print(f"Completed task {task_id}: '{task.description}'")
            else:
                console.print(f"Error: Task with ID {task_id} not found.")
        elif command == "delete":
            if len(args) < 2:
                console.print("Usage: delete <id>")
                continue
            try:
                task_id = int(args[1])
            except ValueError:
                console.print("Error: Task ID must be an integer.")
                continue
            if confirm_delete(task_id):
                if delete_task(task_id):
                    console.print(f"Deleted task {task_id}.")
                else:
                    console.print(f"Error: Task with ID {task_id} not found.")
            else:
                console.print(f"Deletion of task {task_id} cancelled.")
        elif command == "help":
            display_help()
        elif command == "exit":
            console.print("Exiting application. Goodbye!")
            break
        else:
            console.print(f"Unknown command: {command}")

def main():
    """Main entry point for the CLI application."""
    if len(sys.argv) > 1:
        # Non-interactive mode (for backward compatibility or scripting)
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
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
