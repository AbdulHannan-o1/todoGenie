import sys
from commands import add_task, list_tasks, update_task, complete_task, delete_task
from utils import console, display_tasks, confirm_delete
from rich.prompt import Prompt, IntPrompt
from simple_term_menu import TerminalMenu
from rich.panel import Panel
from rich.text import Text

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
        console.clear() # Clear screen at the beginning of each iteration (T039)

        # TODOGENIE Banner (T034)
        console.print(
            Panel(
                Text("TODOGENIE", justify="center", style="bold green"),
                style="bold blue",
                width=console.width
            )
        )

        tasks = list_tasks()
        if tasks: # Conditional Task Display (T035)
            console.print("\n--- Current Tasks ---", style="bold blue")
            display_tasks(tasks)
            console.print("---------------------\n", style="bold blue")
        else:
            console.print("\n--- [yellow]No tasks yet. Add one![/yellow] ---\n")

        menu_entries = [
            "Add a new task",
            "List all tasks",
            "Update a task",
            "Mark a task as complete",
            "Delete a task",
            "Show help",
            "Exit application"
        ]

        terminal_menu = TerminalMenu(
            menu_entries,
            title="Select an option:",
            menu_cursor="> ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("fg_green", "bold"),
            cycle_cursor=True,
            clear_screen=True, # Re-enabled (T038)
            default_menu_index=0 # Default to "Add a new task"
        )
        selected_index = terminal_menu.show()

        if selected_index is None: # User pressed Ctrl+C or Esc
            console.print("[blue]Exiting application. Goodbye![/blue]")
            break

        selected_option = menu_entries[selected_index]

        if selected_option == "Add a new task":
            description = Prompt.ask("Enter task description")
            task = add_task(description)
            console.print(f"[green]Added task: '{task.description}' with ID {task.id}[/green]")
        elif selected_option == "List all tasks":
            # Tasks are already displayed at the beginning of the loop
            pass
        elif selected_option == "Update a task":
            try:
                task_id = IntPrompt.ask("Enter task ID to update")
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                continue
            new_description = Prompt.ask("Enter new description")
            task = update_task(task_id, new_description)
            if task:
                console.print(f"[green]Updated task {task_id} to: '{task.description}'[/green]")
            else:
                console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        elif selected_option == "Mark a task as complete":
            try:
                task_id = IntPrompt.ask("Enter task ID to complete")
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                continue
            task = complete_task(task_id)
            if task:
                console.print(f"[green]Completed task {task_id}: '{task.description}'[/green]")
            else:
                console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        elif selected_option == "Delete a task":
            try:
                task_id = IntPrompt.ask("Enter task ID to delete")
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                continue
            if confirm_delete(task_id):
                if delete_task(task_id):
                    console.print(f"[green]Deleted task {task_id}.[/green]")
                else:
                    console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
            else:
                console.print(f"[yellow]Deletion of task {task_id} cancelled.[/yellow]")
        elif selected_option == "Show help":
            display_help()
        elif selected_option == "Exit application":
            console.print("[blue]Exiting application. Goodbye![/blue]")
            break

def main():
    """Main entry point for the CLI application."""
    if len(sys.argv) > 1:
        # Non-interactive mode (for backward compatibility or scripting)
        command = sys.argv[1]
        if command == "add":
            if len(sys.argv) < 3:
                console.print("[yellow]Usage: python app.py add <description>[/yellow]")
                return
            description = " ".join(sys.argv[2:])
            task = add_task(description)
            console.print(f"[green]Added task: '{task.description}' with ID {task.id}[/green]")
        elif command == "list":
            tasks = list_tasks()
            display_tasks(tasks)
        elif command == "update":
            if len(sys.argv) < 4:
                console.print("[yellow]Usage: python app.py update <id> <new-description>[/yellow]")
                return
            try:
                task_id = int(sys.argv[2])
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                return
            new_description = " ".join(sys.argv[3:])
            task = update_task(task_id, new_description)
            if task:
                console.print(f"[green]Updated task {task_id} to: '{task.description}'[/green]")
            else:
                console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        elif command == "complete":
            if len(sys.argv) < 3:
                console.print("[yellow]Usage: python app.py complete <id>[/yellow]")
                return
            try:
                task_id = int(sys.argv[2])
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                return
            task = complete_task(task_id)
            if task:
                console.print(f"[green]Completed task {task_id}: '{task.description}'[/green]")
            else:
                console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        elif command == "delete":
            if len(sys.argv) < 3:
                console.print("[yellow]Usage: python app.py delete <id>[/yellow]")
                return
            try:
                task_id = int(sys.argv[2])
            except ValueError:
                console.print("[red]Error: Task ID must be an integer.[/red]")
                return
            if confirm_delete(task_id):
                if delete_task(task_id):
                    console.print(f"[green]Deleted task {task_id}.[/green]")
                else:
                    console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
            else:
                console.print(f"[yellow]Deletion of task {task_id} cancelled.[/yellow]")
        elif command == "help":
            display_help()
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()