# SpecComplianceSkill

## Description
This skill ensures that all actions taken during Phase I strictly comply with the project constitution and Phase I specifications.

## Purpose
Acts as a governance and safety check to validate that all implementation decisions align with Phase I constraints.

## Validation Criteria

Before any task operation is executed, this skill validates that:

1. **Phase I Scope Compliance**
   - The feature or change is within Phase I scope
   - No Phase II features are being implemented prematurely
   - Core functionality is prioritized over advanced features

2. **Technology Constraints**
   - No external services are used (no web APIs, cloud services, etc.)
   - No external databases or data stores are used
   - The implementation remains in-memory only
   - Data persistence is file-based (JSON) only when explicitly required

3. **Implementation Type**
   - The application remains a Python console application
   - No GUI, web interface, or mobile app components
   - No complex frameworks or libraries beyond Phase I allowances

## How to Use

Invoke this skill before any implementation task that could potentially violate Phase I constraints:

```
When: Adding new features, modifying architecture, or introducing dependencies
Action: Run SpecComplianceSkill validation
Decision: Proceed only if all validation criteria pass
```

## Governance Role

- This skill does **not** perform business logic
- This skill does **not** make implementation decisions
- This skill **only** validates compliance with constraints
- Use this skill as a safety gate before executing changes

## Example Workflow

```
User: "Let's add a cloud backup feature for tasks"
Assistant: [Invokes SpecComplianceSkill]
Validation Result: ❌ FAILED - External cloud services are not allowed in Phase I
Action: Reject the proposal and suggest Phase I alternatives (e.g., local file export)
```

## Phase I Reference

Refer to the following documents for definitive Phase I requirements:
- `.specify/memory/constitution.md` - Core project principles
- `specs/<feature>/spec.md` - Feature specifications
- Any Phase I constraint documentation
