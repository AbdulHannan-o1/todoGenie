--- 
phr_id: 0033
phr_title: Fix interactive menu redraw and flickering
phr_stage: red
phr_date: 2025-12-07
phr_model: gemini-1.5-flash
phr_feature: 001-cli-task-management
phr_branch: main
phr_user: abdulhannan
phr_command: null
phr_labels: ["ui", "rich", "bugfix", "interactive-menu"]
phr_links: {spec: "specs/001-cli-task-management/spec.md", ticket: "null", adr: "null", pr: "null"}
phr_files_yaml: |
  - src/main.py
phr_tests_yaml: |
  - Manual testing of interactive menu navigation and selection
phr_prompt_text: |
  the app got stuck like this when it try to navgate between the option using arrow keys 
  it pront option on every ress 
  > Add a new task
    Update a task
    Complete a task
    Delete a task
    Show help
    Exit application
    Exit application
  > Add a new task
    Update a task
    Complete a task
  Delete a task
    Show help
    Exit application
  > Add a new task
    Update a task
    Complete a task
    Delete a task
    Show help
    Exit application
  > Add a new task
    Update a task
    Complete a task
    Delete a task
    Show help
    Exit application
  > Add a new task
    Update a task
    Complete a task
    Delete a task
    Show help
    Exit application

  here is how the option should be there 
  Select an option: 
  > Add a new task 
  Update a task 
  Mark a task as complete 
  Delete a task 
  Show help 
  Exit application

  the user user up and down arrow to navigate throw tasks and the > sign move up down according to it
phr_response_text: |
  The user is reporting that the interactive menu is not working as expected. Instead of redrawing in place, it's printing the entire menu again on each arrow key press, leading to a "stuck" and messy output.

  This indicates that the ANSI escape codes for clearing lines and moving the cursor are not being applied correctly, or the terminal is not interpreting them as expected, or there's a fundamental misunderstanding of how `console.print` interacts with raw terminal control.

  Let's re-examine the `get_interactive_menu_selection` function:

  ```python
  def get_interactive_menu_selection(menu_options: List[str], commands: List[str], console: Console) -> str:
      """Displays an interactive menu with arrow key navigation and returns the selected command."""
      selected_index = 0
      num_options = len(menu_options)
      
      # Print "Select an option:" header
      console.print("Select an option:")
      
      # Initial menu render
      for i, option in enumerate(menu_options):
          if i == selected_index:
              console.print(f"[bold green]> {option}[/bold green]")
          else:
              console.print(f"  {option}")
      
      # Move cursor up to the start of the menu options for interaction
      console.file.write(f"{CURSOR_UP * num_options}")
      console.file.flush()

      while True:
          char = readchar.readchar()

          if char == UP_ARROW:
              selected_index = (selected_index - 1) % num_options
          elif char == DOWN_ARROW:
              selected_index = (selected_index + 1) % num_options
          elif char == ENTER:
              # Clear the menu lines before returning
              for _ in range(num_options + 1): # +1 for "Select an option:"
                  console.file.write(f"{CLEAR_LINE}\n")
              console.file.write(f"{CURSOR_UP * (num_options + 1)}") # Move cursor back up
              console.file.flush()
              return commands[selected_index]
          
          # Redraw menu
          console.file.write(f"{CURSOR_UP * num_options}") # Move cursor to start of options
          for i, option in enumerate(menu_options):
              console.file.write(CLEAR_LINE) # Clear current line
              if i == selected_index:
                  console.print(f"[bold green]> {option}[/bold green]", end="\n")
              else:
                  console.print(f"  {option}", end="\n")
          console.file.write(f"{CURSOR_UP * num_options}") # Move cursor back to start of options
          console.file.flush()
  ```

  The core issue is likely that `console.print` (even with `end="\n"`) is adding newlines and potentially not respecting the cursor movements as directly as `sys.stdout.write` would. `rich.console.Console` is designed to render rich text, and its internal buffering and rendering might be interfering with the precise cursor control needed for an interactive menu.

  To achieve the desired in-place redrawing without a full TUI framework, we need to:
  1.  **Directly write to `sys.stdout` for cursor control and clearing.**
  2.  **Use `rich.console.Console.render_str` or similar to get the raw ANSI-escaped string for Rich-formatted text, then print that directly to `sys.stdout`.**

  Let's refine the `get_interactive_menu_selection` function to use `sys.stdout.write` for all terminal manipulations and `console.render_str` for Rich-formatted text.

  Also, the `CLEAR_LINE` should clear the current line *without* moving the cursor. Then we move the cursor to the beginning of the line.

  **Revised `get_interactive_menu_selection` plan:**

  1.  **Initial print:**
      *   Print "Select an option:" using `console.print`.
      *   Print the initial menu using `console.print` for each line.
      *   Keep track of the number of lines printed for the menu (including "Select an option:").

  2.  **Inside the loop:**
      *   When an arrow key is pressed:
          *   Move the cursor up to the start of the menu options (just below "Select an option:").
          *   For each menu option:
              *   Clear the current line using `sys.stdout.write(CLEAR_LINE)`.
              *   Render the Rich-formatted option string (with `>` or ` `) using `console.render_str`.
              *   Write the rendered string to `sys.stdout`.
              *   Write a newline `\n` to `sys.stdout`.
          *   Move the cursor back up to the start of the menu options.
          *   `sys.stdout.flush()` to ensure immediate update.

  3.  **On Enter:**
      *   Move the cursor up to the start of the menu (including "Select an option:").
      *   For each line of the menu (including "Select an option:"):
          *   Clear the line.
          *   Print a newline.
      *   Move the cursor back up to the original position where the menu started.
      *   Return the selected command.

  This approach is more low-level and should give us the precise control needed.

  Let's modify `src/main.py` accordingly.
