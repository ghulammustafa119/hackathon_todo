---
id: 004
title: Create TaskUpdateSkill
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: master
user: user
command: N/A
labels: [skills,tasks,update,crd]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/TaskUpdateSkill.md
tests:
 -
---

## Prompt

TaskUpdateSkill
This skill updates existing todo tasks during Phase I.
It modifies task attributes such as title or description after validating the task identifier.
This skill does not manage task storage directly or handle user interaction.

## Response snapshot

Created `.claude/skills/TaskUpdateSkill.md` — a skill that handles task updates. Validates task_id exists, applies updates to specified fields (title, description, due_date, priority, tags, status), delegates storage to InMemoryStoreSkill. Returns success status and updated task data. Includes error scenarios for missing tasks and empty updates. Excludes storage management, user interaction, status transition validation, and history tracking.

## Outcome

- ✅ Impact: Defined task update workflow with validation and delegation
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created TaskUpdateSkill.md in .claude/skills/
- 🔁 Next prompts: None required
- 🧠 Reflection: Skill created with clear dependency on InMemoryStoreSkill

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
