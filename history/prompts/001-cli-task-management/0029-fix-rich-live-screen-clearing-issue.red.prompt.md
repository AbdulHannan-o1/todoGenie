---
phr_id: 0029
phr_title: Fix Rich.Live screen clearing issue
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
  the banner and options are not there
phr_response_text: |
  The user is reporting that the banner and options are not visible when running the application. This suggests an issue with how `rich.live.Live` is interacting with the initial console output or how the `Prompt.ask` is being displayed.

  Let's re-examine `src/main.py`.

  The banner is printed *before* the `Live` context manager is entered:
  ```python
      console.print(Panel(render_banner(), style="bold green", expand=False))
      console.print("\n[bold blue]Welcome to TODOGENIE! Press 'h' for help.[/bold blue]\n")
  ```
  This should ensure it's printed once.

  The `Live` context manager takes over the screen. Any `console.print` or `Prompt.ask` calls *outside* the `live.update()` might be interfering or being overwritten by the `Live` display.

  The `Prompt.ask` is used for user input:
  ```python
              command = Prompt.ask("Enter command (a/u/c/d/l/h/q)", choices=["a", "u", "c", "d", "l", "h", "q"], default="l").lower()
  ```
  This prompt should appear below the live table.

  It's possible that `screen=True` in `Live` is causing the issue by clearing the entire screen, including the banner, when it starts. If `screen=True` is used, `Live` takes over the entire terminal, clearing previous content. The banner should ideally be part of the `Live` display if `screen=True` is desired, or `screen=False` should be used if the banner is to remain static above the live region.

  Given the requirement "Print the ASCII logo *only once* at the start" and "Under the logo, display a table that: - stays on screen permanently", it implies the banner should be *above* the live-updating region. This means `screen=True` is likely the culprit.

  If `screen=False`, `Live` will only manage a specific region of the terminal, allowing content above it to persist.

  Let's modify `src/main.py` to change `screen=True` to `screen=False` in the `Live` constructor.
---