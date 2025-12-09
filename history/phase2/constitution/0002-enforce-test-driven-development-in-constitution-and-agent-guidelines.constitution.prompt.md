---
id: 0002
title: Enforce Test-Driven Development in Constitution and Agent Guidelines
stage: constitution
date: 2025-12-09
surface: "agent"
model: "gemini"
feature: "none"
branch: "001-task-priority"
user: "user"
command: "ensure the constituition and gemini.md file contaid the tdd (test driven development approach ), before writting the code every possible test should be wrritten to ensure the safe a sn secure and fast development"
labels: [constitution, TDD, testing]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
 - .specify/memory/constitution.md
 - GEMINI.md
tests:
 - none
---

## Prompt

ensure the constituition and gemini.md file contain's the tdd (test driven development approach ), before writting the code every possible test should be wrritten to ensure the safe and secure and fast development

## Response snapshot

Understood. I will update both the `GEMINI.md` agent guidelines and the project's `constitution.md` to formally adopt and enforce a Test-Driven Development (TDD) approach. This ensures that tests are written before the implementation code for all new features and bug fixes.

## Outcome

- ✅ Impact: Updated the project's constitution and the agent's operational guidelines to mandate a strict Test-Driven Development (TDD) workflow.
- 🧪 Tests: No tests were run as this was a documentation and process change.
- 📁 Files: 
  - Modified `.specify/memory/constitution.md` to include TDD as a core principle.
  - Modified `GEMINI.md` to include a TDD mandate for the agent.
- 🔁 Next prompts: The user can now proceed with development, and the agent will follow the TDD (Red-Green-Refactor) cycle.
- 🧠 Reflection: This change codifies a best practice, making the development process more robust and ensuring all new code is verifiable by default.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment: n/a
