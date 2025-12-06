import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static, DataTable
from textual.containers import Vertical, Horizontal, Container
from textual.screen import Screen
from rich.panel import Panel
from rich.text import Text
# from rich.table import Table # No longer needed

from commands import add_task, list_tasks, update_task, complete_task, delete_task
from utils import console, confirm_delete # console will be replaced by self.app.console

class TodoBanner(Static):
    """A widget to display the TODOGENIE banner."""
    def render(self) -> Panel:
        return Panel(
            Text("TODOGENIE", justify="center", style="bold green"),
            style="bold blue",
            width=self.app.console.width,
            padding=(1, 0) # Add vertical padding
        )

class TaskListDisplay(DataTable): # Inherit from DataTable
    """A widget to display the list of tasks."""
    def on_mount(self) -> None:
        self.add_columns("ID", "Description", "Status") # Define columns
        self.update_tasks()

    def update_tasks(self) -> None:
        self.clear() # Clear existing rows
        tasks = list_tasks()
        if tasks:
            for task in tasks:
                self.add_row(str(task.id), task.description, task.status)
        else:
            # Display a message if no tasks, DataTable doesn't have a direct "empty" state message
            # We might need a separate Static for this or handle it in the parent compose
            pass # For now, just clear the table

class StatusBar(Static):
    """A widget to display dynamic status messages."""
    def on_mount(self) -> None:
        self.update("Welcome to TodoGenie!")

    def update_message(self, message: str, style: str = "none") -> None:
        self.update(Text(message, style=style))

class TodoApp(App):
    """Our TUI Todo Application."""

    CSS_PATH = "todo.css" # Link CSS file

    BINDINGS = [
        ("a", "add_task_prompt", "Add Task"),
        ("l", "list_tasks_action", "List Tasks"),
        ("u", "update_task_prompt", "Update Task"),
        ("c", "complete_task_prompt", "Complete Task"),
        ("d", "delete_task_prompt", "Delete Task"),
        ("h", "show_help", "Help"),
        ("q", "quit_app", "Quit")
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield TodoBanner()
        yield TaskListDisplay() # Keep TaskListDisplay
        yield StatusBar() # Integrate StatusBar
        yield Footer() # Footer will display key bindings

    def action_add_task_prompt(self) -> None:
        self.app.push_screen(AddTaskScreen())

    def action_list_tasks_action(self) -> None:
        self.query_one(TaskListDisplay).update_tasks()

    def action_update_task_prompt(self) -> None:
        self.app.push_screen(UpdateTaskScreen())

    def action_complete_task_prompt(self) -> None:
        self.app.push_screen(CompleteTaskScreen())

    def action_delete_task_prompt(self) -> None:
        self.app.push_screen(DeleteTaskScreen())

    def action_show_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when a row is selected in the DataTable."""
        row_key = event.row_key
        row_data = self.query_one(DataTable).get_row(row_key)
        self.query_one(StatusBar).update_message(f"Selected Task ID: {row_data[0]} - {row_data[1]}", style="blue")


class AddTaskScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Add New Task", classes="title"),
            Input(placeholder="Task description", id="add_description_input"),
            Button("Add", variant="primary", id="add_task_button"),
            Button("Cancel", variant="default", id="cancel_button")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_task_button":
            description_input = self.query_one("#add_description_input", Input)
            description = description_input.value
            if description:
                add_task(description)
                self.app.pop_screen()
                self.app.query_one(TaskListDisplay).update_tasks()
                self.app.query_one(StatusBar).update_message(f"Added task: '{description}'", style="green")
            else:
                self.query_one(".title", Static).update("Add New Task [red]Description cannot be empty[/red]")
        elif event.button.id == "cancel_button":
            self.app.pop_screen()

class UpdateTaskScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Update Task", classes="title"),
            Input(placeholder="Task ID", id="update_id_input"),
            Input(placeholder="New description", id="update_description_input"),
            Button("Update", variant="primary", id="update_task_button"),
            Button("Cancel", variant="default", id="cancel_button")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update_task_button":
            task_id_input = self.query_one("#update_id_input", Input)
            description_input = self.query_one("#update_description_input", Input)
            try:
                task_id = int(task_id_input.value)
                new_description = description_input.value
                if new_description:
                    task = update_task(task_id, new_description)
                    if task:
                        self.app.pop_screen()
                        self.app.query_one(TaskListDisplay).update_tasks()
                        self.app.query_one(StatusBar).update_message(f"Updated task {task_id} to: '{new_description}'", style="green")
                    else:
                        self.query_one(".title", Static).update(f"Update Task [red]Task with ID {task_id} not found[/red]")
                        self.app.query_one(StatusBar).update_message(f"Error: Task with ID {task_id} not found.", style="red")
                else:
                    self.query_one(".title", Static).update("Update Task [red]Description cannot be empty[/red]")
                    self.app.query_one(StatusBar).update_message("Error: Description cannot be empty.", style="red")
            except ValueError:
                self.query_one(".title", Static).update("Update Task [red]Task ID must be an integer[/red]")
                self.app.query_one(StatusBar).update_message("Error: Task ID must be an integer.", style="red")
        elif event.button.id == "cancel_button":
            self.app.pop_screen()

class CompleteTaskScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Complete Task", classes="title"),
            Input(placeholder="Task ID", id="complete_id_input"),
            Button("Complete", variant="primary", id="complete_task_button"),
            Button("Cancel", variant="default", id="cancel_button")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "complete_task_button":
            task_id_input = self.query_one("#complete_id_input", Input)
            try:
                task_id = int(task_id_input.value)
                task = complete_task(task_id)
                if task:
                    self.app.pop_screen()
                    self.app.query_one(TaskListDisplay).update_tasks()
                    self.app.query_one(StatusBar).update_message(f"Completed task {task_id}: '{task.description}'", style="green")
                else:
                    self.query_one(".title", Static).update(f"Complete Task [red]Task with ID {task_id} not found[/red]")
                    self.app.query_one(StatusBar).update_message(f"Error: Task with ID {task_id} not found.", style="red")
            except ValueError:
                self.query_one(".title", Static).update("Complete Task [red]Task ID must be an integer[/red]")
                self.app.query_one(StatusBar).update_message("Error: Task ID must be an integer.", style="red")
        elif event.button.id == "cancel_button":
            self.app.pop_screen()

class DeleteTaskScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Delete Task", classes="title"),
            Input(placeholder="Task ID", id="delete_id_input"),
            Button("Delete", variant="error", id="delete_task_button"),
            Button("Cancel", variant="default", id="cancel_button")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete_task_button":
            task_id_input = self.query_one("#delete_id_input", Input)
            try:
                task_id = int(task_id_input.value)
                if confirm_delete(task_id): # This will still use rich.prompt.Confirm
                    if delete_task(task_id):
                        self.app.pop_screen()
                        self.app.query_one(TaskListDisplay).update_tasks()
                        self.app.query_one(StatusBar).update_message(f"Deleted task {task_id}.", style="green")
                    else:
                        self.query_one(".title", Static).update(f"Delete Task [red]Task with ID {task_id} not found[/red]")
                        self.app.query_one(StatusBar).update_message(f"Error: Task with ID {task_id} not found.", style="red")
                else:
                    self.query_one(".title", Static).update(f"Delete Task [yellow]Deletion of task {task_id} cancelled[/yellow]")
                    self.app.query_one(StatusBar).update_message(f"Deletion of task {task_id} cancelled.", style="yellow")
            except ValueError:
                self.query_one(".title", Static).update("Delete Task [red]Task ID must be an integer[/red]")
                self.app.query_one(StatusBar).update_message("Error: Task ID must be an integer.", style="red")
        elif event.button.id == "cancel_button":
            self.app.pop_screen()

class HelpScreen(Screen):
    def compose(self) -> ComposeResult:
        help_message = """
Commands:
  a - Add a new task
  l - List all tasks
  u - Update a task
  c - Mark a task as complete
  d - Delete a task
  h - Show this help message
  q - Quit application
"""
        yield Vertical(
            Static("Help", classes="title"),
            Static(help_message),
            Button("Back", variant="primary", id="back_button")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()

if __name__ == "__main__":
    app = TodoApp()
    app.run()