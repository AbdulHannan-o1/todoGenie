---
id: 0009
title: Implement Arrow-Key Navigable Menu
stage: refactor
date: 2025-12-06
surface: agent
model: (unknown)
feature: 001-cli-task-management
branch: app-core
user: abdulhannan
command: "The user is now requesting a more advanced interactive UI. They want:
1.  An arrow (`>`) in green color to indicate the currently selected option in the menu.
2.  The ability to navigate the menu using arrow keys (up/down).
3.  Selection of an option by hitting Enter, without needing to type a number.
4.  The default selection should be "add".

This is a significant change from the current `rich.prompt.IntPrompt` which only allows numerical input. `rich` itself does not directly provide a widget for arrow-key navigable menus out-of-the-box for this kind of interactive loop. Implementing this would typically require:
*   Using a library like `curses` (for full-screen terminal applications) or `prompt_toolkit` (which `rich` itself uses internally for some prompts, but doesn't expose this level of menu control directly).
*   Manually handling key presses, redrawing the terminal, and managing the cursor position.

This is a much more complex UI implementation than what has been done so far and goes beyond simple `rich.console` and `rich.prompt` usage. It would require a substantial refactoring of the interactive loop and potentially introducing a new dependency.

I need to explain this limitation to the user and propose a more feasible alternative within the current `rich` framework, or inform them that this would require a more complex solution.

However, before I do that, I should check if there's any `rich` component or a simple workaround I might be missing that could achieve this. I will search the `rich` documentation for "menu", "selection", "arrow keys", "interactive list"."
labels: [refactor, cli, interactive-mode, menu, ui]
links:
  spec: specs/001-cli-task-management/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - app.py
  - specs/001-cli-task-management/tasks.md
  - specs/001-cli-task-management/plan.md
  - README.md
tests:
  - none
---

## Prompt

```text
it should be like user have a list of options to select throught for example :
1 add
> 2 list 

in the above example user slected the 2nd task nad when hi hit enter it should do its job no need to take input like this 

--- Current Tasks ---
            Tasks            
┏━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Description ┃ Status ┃
┡━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
└────┴─────────────┴────────┘
---------------------


--- Menu ---
1. Add a new task
2. List all tasks
3. Update a task
4. Mark a task as complete
5. Delete a task
6. Show help
7. Exit application
------------
Select an option [1/2/3/4/5/6/7] (1):
```

## Response snapshot

The interactive CLI now features an arrow-key navigable menu with a visual indicator, enhancing user experience.

## Outcome

- ✅ Impact: The interactive CLI now features an arrow-key navigable menu with a visual indicator, enhancing user experience.
- 🧪 Tests: No explicit tests were defined or run for this implementation.
- 📁 Files: Modified 4 files.
- 🔁 Next prompts: User can now test the updated interactive application or request further enhancements.
- 🧠 Reflection: Successfully integrated `simple-term-menu` to provide the requested arrow-key navigation and visual feedback.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): None
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None