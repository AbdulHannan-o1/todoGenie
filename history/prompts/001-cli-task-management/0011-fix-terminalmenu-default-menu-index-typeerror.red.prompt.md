---
id: 0011
title: Fix TerminalMenu default_menu_index TypeError
stage: red
date: 2025-12-06
surface: agent
model: (unknown)
feature: 001-cli-task-management
branch: app-core
user: abdulhannan
command: "The user is reporting another `TypeError`, this time for `default_menu_index`.
This means that the `default_menu_index` keyword argument is not recognized by the installed version of `simple-term-menu`.

I need to check the `simple-term-menu` documentation again for how to set the default selected item. It's possible the parameter name is different or the functionality is not directly exposed as a keyword argument.

I will search the `simple-term-menu` documentation for "default selection", "initial selection", "start index"."
labels: [bugfix, cli, interactive-mode, menu, ui, typeerror]
links:
  spec: specs/001-cli-task-management/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - app.py
tests:
  - none
---

## Prompt

```text
(venv) abdulhannan@fedora:~/data/development/openAi/todo-in-memory-app$ source venv/bin/activate 
(venv) abdulhannan@fedora:~/data/development/openAi/todo-in-memory-app$ python app.py

--- Current Tasks ---
            Tasks            
┏━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Description ┃ Status ┃
┡━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
└────┴─────────────┴────────┘
---------------------

Traceback (most recent call last):
  File "/home/abdulhannan/data/development/openAi/todo-in-memory-app/app.py", line 177, in <module>
    main()
    ~~~~^^
  File "/home/abdulhannan/data/development/openAi/todo-in-memory-app/app.py", line 174, in main
    interactive_mode()
    ~~~~~~~~~~~~~~~~^^
  File "/home/abdulhannan/data/development/openAi/todo-in-memory-app/app.py", line 39, in interactive_mode
    terminal_menu = TerminalMenu(
        menu_entries,
    ...<6 lines>...
        default_menu_index=0 # Default to "Add a new task"
    )
TypeError: TerminalMenu.__init__() got an unexpected keyword argument 'default_menu_index'
(venv) abdulhannan@fedora:~/data/development/openAi/todo-in-memory-app$ 
```

## Response snapshot

Resolved `TypeError` related to `default_menu_index` in `TerminalMenu` by using `cursor_index`.

## Outcome

- ✅ Impact: Resolved `TypeError` related to `default_menu_index` in `TerminalMenu` by using `cursor_index`.
- 🧪 Tests: No explicit tests were defined or run for this fix.
- 📁 Files: Modified 1 file.
- 🔁 Next prompts: User can now test the application to confirm the fix.
- 🧠 Reflection: The `simple-term-menu` library uses `cursor_index` instead of `default_menu_index` for setting the initial selection.

## Evaluation notes (flywheel)

- Failure modes observed: `TypeError` due to incorrect parameter name.
- Graders run and results (PASS/FAIL): None
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None