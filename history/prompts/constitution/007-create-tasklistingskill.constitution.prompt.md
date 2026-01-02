---
id: 007
title: Create TaskListingSkill
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: master
user: user
command: N/A
labels: [skills,tasks,listing,retrieval]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/TaskListingSkill.md
tests:
 -
---

## Prompt

TaskListingSkill
This skill retrieves all todo tasks from the in-memory store and prepares them for display.
It does not perform sorting, filtering, or advanced formatting beyond Phase I requirements.

## Response snapshot

Created `.claude/skills/TaskListingSkill.md` — a skill that retrieves all tasks from in-memory store. Returns raw task list with count, no parameters required. Provides full task objects in storage order. Excludes sorting, filtering, grouping, formatting, pagination, and user interaction. Clear separation between data retrieval (this skill) and display formatting (presentation layer). Includes examples for normal, empty store, and error scenarios.

## Outcome

- ✅ Impact: Defined task retrieval workflow with clear scope boundaries
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created TaskListingSkill.md in .claude/skills/
- 🔁 Next prompts: None required
- 🧠 Reflection: Skill created with clear dependency on InMemoryStoreSkill

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
