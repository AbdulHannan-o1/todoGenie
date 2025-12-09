---
phr_id: 0030
phr_title: Fix Rich.Live prompt visibility issue
phr_stage: red
phr_date: 2025-12-07
phr_model: gemini-1.5-flash
phr_feature: 001-cli-task-management
phr_branch: main
phr_user: abdulhannan
phr_command: null
phr_labels: ["ui", "rich", "bugfix"]
phr_links: {spec: "specs/001-cli-task-management/spec.md", ticket: "null", adr: "null", pr: "null"}
phr_files_yaml: |
  - src/main.py
phr_tests_yaml: |
  - Manual testing of UI persistence and task operations
phr_prompt_text: |
  the banner is back but options wont
phr_response_text: |
  The user is reporting that the banner is back, but the "options" (referring to the command prompt and potentially the help message) are not displaying correctly.

  This indicates that while `screen=False` fixed the banner being cleared, there might still be an issue with how `Prompt.ask` interacts within the `Live` context, or how messages are being displayed.

  Let's re-examine the `main_loop` in `src/main.py`:

  ```python
  def main_loop():
      """Main application loop using Rich.Live."""
      console.print(Panel(render_banner(), style="bold green", expand=False))
      console.print("\n[bold blue]Welcome to TODOGENIE! Press 'h' for help.[/bold blue]\n")

      with Live(render_table(list_tasks()), screen=False, refresh_per_second=4) as live:
          while True:
              command = Prompt.ask("Enter command (a/u/c/d/l/h/q)", choices=["a", "u", "c", "d", "l", "h", "q"], default="l").lower()
              # ... rest of the command handling ...
              live.update(render_table(list_tasks()))
  ```

  The `Prompt.ask` is indeed inside the `while True` loop, which is within the `Live` context. When `screen=False`, `Live` manages a region, and `Prompt.ask` should typically print below that region.

  However, `rich.live.Live` can sometimes interfere with `Prompt.ask` if not handled carefully, especially if the `Live` display is constantly refreshing. The `refresh_per_second=4` might be causing the prompt to flicker or be overwritten.

  A common pattern when using `Prompt.ask` with `Live` is to temporarily stop the `Live` display, get the input, and then resume the `Live` display.

  Let's try modifying the `main_loop` to pause the `Live` display before asking for input and resume it afterward.

  The `Live` object has `stop()` and `start()` methods.

  ```python
  def main_loop():
      """Main application loop using Rich.Live."""
      console.print(Panel(render_banner(), style="bold green", expand=False))
      console.print("\n[bold blue]Welcome to TODOGENIE! Press 'h' for help.[/bold blue]\n")

      with Live(render_table(list_tasks()), screen=False, refresh_per_second=4) as live:
          while True:
              live.stop() # Stop the live display temporarily
              command = Prompt.ask("Enter command (a/u/c/d/l/h/q)", choices=["a", "u", "c", "d", "l", "h", "q"], default="l").lower()
              live.start() # Resume the live display
              # ... rest of the command handling ...
              live.update(render_table(list_tasks()))
  ```

  This approach should ensure that the `Prompt.ask` gets a clear line to display and receive input without being immediately overwritten by the `Live` table's refresh.

  I will apply this change to `src/main.py`.
---
