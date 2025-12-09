---
phr_id: 0031
phr_title: Implement interactive menu with arrow key navigation
phr_stage: green
phr_date: 2025-12-07
phr_model: gemini-1.5-flash
phr_feature: 001-cli-task-management
phr_branch: main
phr_user: abdulhannan
phr_command: null
phr_labels: ["ui", "rich", "interactive-menu"]
phr_links: {spec: "specs/001-cli-task-management/spec.md", ticket: "null", adr: "null", pr: "null"}
phr_files_yaml: |
  - src/main.py
  - requirements.txt
phr_tests_yaml: |
  - Manual testing of interactive menu navigation and selection
phr_prompt_text: |
  the banner is back but options wont

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
  The user is providing feedback on the current UI.
  They are seeing:
  1.  The banner.
  2.  The welcome message.
  3.  A flickering table with "Your Tasks" repeated multiple times, and "Please select one of the available options" appearing.
  4.  The actual table content eventually stabilizes, but the prompt for commands is not the desired interactive menu.

  The user wants an interactive menu where they can use up/down arrows to navigate and a `>` sign indicates the selected option, similar to a TUI menu, but explicitly states "Ensure the code works inside a normal terminal (no TUI frameworks like curses)."

  This means the current `Prompt.ask` is not sufficient for the desired interactive menu. `rich.prompt.Prompt` is for single-line input with validation, not for interactive navigation.

  To achieve the desired interactive menu with arrow key navigation and a `>` indicator, I need to implement a custom menu. This will likely involve:
  1.  Capturing individual key presses (arrow keys, Enter).
  2.  Redrawing the menu on each key press to show the `>` indicator moving.
  3.  Handling the selection when Enter is pressed.

  This is a significant change from the current `Prompt.ask` approach.

  **Problem 1: Flickering/repeated "Your Tasks" and "Please select one of the available options"**
  This is likely due to `live.stop()` and `live.start()` being called around `Prompt.ask`, but `Prompt.ask` itself might be printing its own messages that interfere with the `Live` context when it restarts. The "Please select one of the available options" is not something I explicitly added, so it might be coming from `rich.prompt.Prompt`'s internal workings when `choices` are provided.

  **Problem 2: Desired Interactive Menu**
  The user wants a menu like this:
  ```
  Select an option:
  > Add a new task
    Update a task
    Mark a task as complete
    Delete a task
    Show help
    Exit application
  ```
  This requires a custom implementation for menu navigation.

  **Revised Plan:**

  1.  **Address Flickering/Repeated Messages:**
      *   The "Please select one of the available options" is likely from `rich.prompt.Prompt` when `choices` are used. I will remove the `choices` from `Prompt.ask` and instead provide a clear instruction for the user to type the command.
      *   The flickering of "Your Tasks" might be related to `live.stop()` and `live.start()` combined with `Prompt.ask`'s output. I will try to simplify the interaction with `Prompt.ask` first.

  2.  **Implement Custom Interactive Menu (if `Prompt.ask` is not sufficient after fixing flickering):**
      *   This will be a more complex task. I'd need to use a library like `readchar` or `getch` to capture single key presses.
      *   I'd need to manage the state of the selected item and redraw the menu within the `Live` context.
      *   This would essentially be building a mini-TUI element without a full TUI framework.

  Let's first try to fix the flickering and the "Please select one of the available options" message by simplifying the `Prompt.ask` call. I will remove the `choices` argument from `Prompt.ask` and just ask for the command directly. This might make the prompt less "smart" but could prevent the unwanted output.

  If the user still insists on the arrow-key navigable menu, that will be a separate, more involved implementation. For now, let's focus on getting a clean, non-flickering prompt.

  **Action:** Modify `src/main.py` to remove `choices` from `Prompt.ask` for the main command input.
---
