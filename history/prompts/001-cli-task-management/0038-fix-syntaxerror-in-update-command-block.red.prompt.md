---
phr_id: 0038
phr_title: Fix SyntaxError in update command block
phr_stage: red
phr_date: 2025-12-07
phr_model: gemini-1.5-flash
phr_feature: 001-cli-task-management
phr_branch: main
phr_user: abdulhannan
phr_command: null
phr_labels: ["bugfix", "syntax"]
phr_links: {spec: "specs/001-cli-task-management/spec.md", ticket: "null", adr: "null", pr: "null"}
phr_files_yaml: |
  - src/main.py
phr_tests_yaml: |
  - Manual testing of update command
phr_prompt_text: |
  (venv) abdulhannan@fedora:~/data/development/openAi/todogenie$ python src/main.py
    File "/home/abdulhannan/data/development/openAi/todogenie/src/main.py", line 203
      elif command == 'c':
      ^^^^
  SyntaxError: invalid syntax
  (venv) abdulhannan@fedora:~/data/development/openAi/todogenie$
phr_response_text: |
  The user is reporting a `SyntaxError: invalid syntax` on line 203, specifically at `elif command == 'c':`.

  This error typically occurs when there's an unmatched parenthesis, bracket, or an incomplete statement in the preceding lines of code. Python's `SyntaxError` often points to the line *after* the actual error.

  Let's look at the code around line 203 in `src/main.py`. The relevant section is likely within the `main_loop` function, specifically the `elif command == 'u':` block, as the `elif command == 'c':` immediately follows it.

  ```python
              elif command == 'u':
                  with live.pause(): # Pause live rendering for prompts
                      task_id_str = Prompt.ask("Enter task ID to update")
                      try:
                          task_id = int(task_id_str)
                      except ValueError:
                          console.print("[red]Invalid Task ID. Please enter a number.[/red]")
                          continue
                      
                      new_description = Prompt.ask("Enter new description")
                      if not new_description:
                          console.print("[red]New description cannot be empty.[/red]")
                          continue
                      
                      task = update_task(task_id, new_description)
                      if task:
                          console.print(f"[green]Updated task {task_id}.[/green]")
                      else:
  print("[red]Task with ID {task_id} not found.[/red]") # <--- This line is the culprit!
                  
                  elif command == 'c': # Line 203
                      # ... rest of the code ...
  ```

  Ah, I see the problem! In the `elif command == 'u':` block, the `else:` statement for `if task:` is missing `console.` before `print`. It should be `console.print(...)` instead of `print(...)`.

  This missing `console.` makes the `print` statement an incomplete expression, leading to a `SyntaxError` on the subsequent `elif` line.

  **Fix:** Change `print("[red]Task with ID {task_id} not found.[/red]")` to `console.print("[red]Task with ID {task_id} not found.[/red]")`.

  I will apply this fix to `src/main.py`.
---
