---
id: 006
title: Create TaskCompletionSkill
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: master
user: user
command: N/A
labels: [skills,tasks,completion,status]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/TaskCompletionSkill.md
tests:
 -
---

## Prompt

TaskCompletionSkill
This skill toggles the completion status of a todo task during Phase I.
It ensures the task state is updated consistently in the in-memory store.
This skill does not perform user input handling or output formatting.

## Response snapshot

Created `.claude/skills/TaskCompletionSkill.md` — a skill that handles task completion status toggling. Validates task_id exists, toggles between pending/completed or accepts explicit status (pending/in_progress/completed), updates via InMemoryStoreSkill, returns success with old and new status. Includes status transition table and error scenarios. Excludes user input handling, output formatting, business logic, and progress tracking.

## Outcome

- ✅ Impact: Defined task completion workflow with flexible status management
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created TaskCompletionSkill.md in .claude/skills/
- 🔁 Next prompts: None required
- 🧠 Reflection: Skill created with clear dependency on InMemoryStoreSkill

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
