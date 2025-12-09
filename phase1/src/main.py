import sys
from typing import List
import readchar
from rich.console import Console, Group
from rich.table import Table
from rich.text import Text
from rich.live import Live
from pyfiglet import Figlet

from .commands import add_task, list_tasks, update_task, complete_task, delete_task
from .models import Priority, Task

console = Console()

# ---------------------------
# Key Definitions
# ---------------------------
KEY_UP = '\x1b[A'
KEY_DOWN = '\x1b[B'
KEY_ENTER = ['\r', '\n']
KEY_BACKSPACE = '\x7f'

# ---------------------------
# Banner and Table
# ---------------------------
def render_banner() -> Text:
    figlet = Figlet(font="standard")
    return Text(figlet.renderText("TODOGENIE"), style="bold green")

def render_table(tasks: List[Task]) -> Table:
    table = Table(title="Your Tasks", show_lines=True, border_style="blue")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Status", style="blue")
    table.add_column("Priority", style="red")

    if not tasks:
        table.add_row("", "", "[yellow]No tasks yet. Add one![/yellow]", "", "")
        return table

    for task in tasks:
        priority_style = {
            Priority.HIGH: "bold red",
            Priority.MEDIUM: "bold yellow",
            Priority.LOW: "bold green",
            Priority.NONE: "dim white",
        }[task.priority]

        status_style = "green" if task.status == "completed" else "yellow"

        table.add_row(
            str(task.id),
            task.title,
            task.description,
            Text(task.status, style=status_style),
            Text(task.priority.value, style=priority_style)
        )
    return table

# ---------------------------
# Menu Rendering with Highlight
# ---------------------------
menu_options = [
    "Add Task",
    "Update Task",
    "Complete Task",
    "Delete Task",
    "List/Refresh Tasks",
    "Show Help",
    "Exit Application",
]
commands_map = ["a", "u", "c", "d", "l", "h", "q"]

def render_menu(selected_index: int) -> Text:
    menu_text = ""
    for i, option in enumerate(menu_options):
        if i == selected_index:
            # Entire line, including > and number, is green
            menu_text += f"[bold green]> {i+1} {option}[/bold green]\n"
        else:
            # Normal line, aligned with spaces
            menu_text += f"  {i+1} {option}\n"
    return Text.from_markup(menu_text)  # <- Use from_markup to render colors


# ---------------------------
# Input (No Border)
# ---------------------------
def render_input_panel(prompt_text: str, current_input: str) -> Text:
    return Text(f"{prompt_text}{current_input}", style="magenta")

# ---------------------------
# Helper to get Priority
# ---------------------------
def priority_from_string(priority_input: str) -> Priority:
    try:
        return Priority[priority_input.strip().upper()]
    except:
        return Priority.NONE

# ---------------------------
# Main Loop
# ---------------------------
def main_loop():
    selected_index = 0
    tasks = list_tasks()
    input_mode = None  # None or add/update/complete/delete step
    input_text = ""
    temp_data = {}  # Store temporary info like title, description, task_id
    prompt_text = ""

    def update_live():
        # Only include input if needed
        panels = [render_banner(), render_table(tasks), render_menu(selected_index)]
        if input_mode is not None:
            panels.append(render_input_panel(prompt_text, input_text))
        live.update(Group(*panels))

    with Live(Group(render_banner(), render_table(tasks), render_menu(selected_index)), screen=True, refresh_per_second=10) as live:
        while True:
            key = readchar.readkey()

            # ---------------- Navigation ----------------
            if input_mode is None:
                if key == KEY_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif key == KEY_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif key in KEY_ENTER:
                    command = commands_map[selected_index]
                    if command == "a":
                        input_mode = "add_title"
                        input_text = ""
                        prompt_text = "Enter task title: "
                    elif command == "u":
                        input_mode = "update_id"
                        input_text = ""
                        prompt_text = "Enter task ID to update: "
                    elif command == "c":
                        input_mode = "complete_id"
                        input_text = ""
                        prompt_text = "Enter task ID to complete: "
                    elif command == "d":
                        input_mode = "delete_id"
                        input_text = ""
                        prompt_text = "Enter task ID to delete: "
                    elif command == "h":
                        console.print(
                            "[bold]Commands:[/bold]\n"
                            "  [cyan]a[/cyan]: Add Task\n"
                            "  [cyan]u[/cyan]: Update Task\n"
                            "  [cyan]c[/cyan]: Complete Task\n"
                            "  [cyan]d[/cyan]: Delete Task\n"
                            "  [cyan]l[/cyan]: List Tasks\n"
                            "  [cyan]h[/cyan]: Show Help\n"
                            "  [cyan]q[/cyan]: Quit",
                        )
                    elif command == "l":
                        tasks = list_tasks()
                    elif command == "q":
                        console.print("[bold red]Exiting TODOGENIE. Goodbye![/bold red]")
                        sys.exit(0)

            # ---------------- Input Mode ----------------
            else:
                if key in KEY_ENTER:
                    # ---- ADD TASK ----
                    if input_mode == "add_title":
                        temp_data["title"] = input_text.strip()
                        input_mode = "add_description"
                        prompt_text = "Enter task description (optional): "
                        input_text = ""
                    elif input_mode == "add_description":
                        temp_data["description"] = input_text.strip()
                        input_mode = "add_priority"
                        prompt_text = "Enter priority (Low, Medium, High, None): "
                        input_text = ""
                    elif input_mode == "add_priority":
                        temp_data["priority"] = priority_from_string(input_text.strip())
                        add_task(temp_data["title"], temp_data["description"], temp_data["priority"])
                        tasks = list_tasks()
                        input_mode = None
                        input_text = ""
                        temp_data.clear()
                        prompt_text = ""

                    # ---- UPDATE TASK ----
                    elif input_mode == "update_id":
                        try:
                            temp_data["task_id"] = int(input_text.strip())
                            input_mode = "update_desc"
                            prompt_text = "Enter new description: "
                            input_text = ""
                        except:
                            console.print("[red]Invalid Task ID[/red]")
                            input_mode = None
                            input_text = ""
                            prompt_text = ""
                    elif input_mode == "update_desc":
                        updated = update_task(temp_data["task_id"], input_text.strip())
                        if updated:
                            console.print(f"[green]Task {temp_data['task_id']} updated![/green]")
                        else:
                            console.print(f"[red]Task {temp_data['task_id']} not found![/red]")
                        tasks = list_tasks()
                        input_mode = None
                        input_text = ""
                        temp_data.clear()
                        prompt_text = ""

                    # ---- COMPLETE TASK ----
                    elif input_mode == "complete_id":
                        try:
                            task_id = int(input_text.strip())
                            completed = complete_task(task_id)
                            if completed:
                                console.print(f"[green]Task {task_id} completed![/green]")
                            else:
                                console.print(f"[red]Task {task_id} not found![/red]")
                        except:
                            console.print("[red]Invalid Task ID[/red]")
                        tasks = list_tasks()
                        input_mode = None
                        input_text = ""
                        prompt_text = ""

                    # ---- DELETE TASK ----
                    elif input_mode == "delete_id":
                        try:
                            temp_data["task_id"] = int(input_text.strip())
                            input_mode = "delete_confirm"
                            prompt_text = f"Are you sure to delete task {temp_data['task_id']}? (yes/no): "
                            input_text = ""
                        except ValueError:
                            console.print("[red]Invalid Task ID[/red]")
                            input_mode = None
                            input_text = ""
                            prompt_text = ""
                    elif input_mode == "delete_confirm":
                        confirm = input_text.strip().lower()
                        if confirm == "yes":
                            deleted = delete_task(temp_data["task_id"])
                            if deleted:
                                console.print(f"[green]Task {temp_data['task_id']} deleted![/green]")
                            else:
                                console.print(f"[red]Task {temp_data['task_id']} not found![/red]")
                        else:
                            console.print("[yellow]Deletion cancelled[/yellow]")
                        tasks = list_tasks()
                        input_mode = None
                        input_text = ""
                        temp_data.clear()
                        prompt_text = ""

                elif key == KEY_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += key

            # Refresh Live
            panels = [render_banner(), render_table(tasks), render_menu(selected_index)]
            if input_mode:
                panels.append(render_input_panel(prompt_text, input_text))
            live.update(Group(*panels))

# ---------------------------
if __name__ == "__main__":
    main_loop()
