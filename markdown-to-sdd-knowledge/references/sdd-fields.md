# SDD Template Field Mapping

This document maps each section of the knowledge files to the specific fields
in the SDD templates. Use this to ensure each knowledge file contains exactly
what downstream agents need — no more, no less.

## How to Use This Reference

When writing a knowledge file section, check the corresponding SDD template
field to understand the shape of the downstream consumption. The goal is
for a downstream agent to be able to fill the SDD template field by reading
only the knowledge file — without going back to the source.

---

## requirements.md → spec.md + test_plan.md

### requirements.md §Problem Statement
Feeds `spec.md`:
- `# [Feature Name]` (title)
- Implicitly informs the entire spec's scope and framing

### requirements.md §User Story
Feeds `spec.md`:
- `## User Story` → `As a [user], I want [goal] so that [reason].`

### requirements.md §Functional Requirements
Feeds `spec.md`:
- `### Happy Path` → `Given [precondition], when [action], then [outcome]`
- Each functional requirement is a candidate for one or more acceptance criteria

Feeds `test_plan.md`:
- `## Unit Tests` → each functional requirement maps to a test scenario
- `## Integration / UI` → end-to-end coverage of functional requirements

### requirements.md §Non-Functional Requirements
Feeds `spec.md`:
- `## Non-Functional Requirements` → Performance, Accessibility, Offline fields

Feeds `test_plan.md`:
- Non-functional requirements that are testable (e.g., "p99 < 100ms") become
  boundary tests

### requirements.md §Acceptance Criteria
Feeds `spec.md` directly:
- `### Happy Path` → `Given [precondition], when [action], then [outcome]`
- `### Edge Cases / Error Handling` → `When [error condition], then [fallback]`

Feeds `test_plan.md` directly:
- `## Edge Cases` → each edge case is a test scenario

---

## approach.md → plan.md + tasks.md

### approach.md §Tech Context
Feeds `plan.md`:
- `## Approach` (informs technical strategy description)
- `## Dependencies` (tech stack dependencies)

### approach.md §Files Referenced
Feeds `plan.md`:
- `touches:` frontmatter → list of file paths
- `## Files to Create / Change` → Action | File | Rationale table

Feeds `tasks.md`:
- `## Block N: [Category]` → task descriptions reference these files

### approach.md §Dependencies
Feeds `plan.md`:
- `depends_on:` frontmatter → feature IDs
- `## Dependencies`

### approach.md §Risks
Feeds `plan.md`:
- `## Risks`

### approach.md §Constraints
Feeds `plan.md`:
- `## Risks` (constraints often manifest as risks)
- `## Approach` (constraints shape technical decisions)

Feeds `tasks.md`:
- Constraints may dictate task ordering or blocks

---

## ux-ui.md → spec.md

### ux-ui.md §Screens / Views + §Interactions + §Visual Details
Feeds `spec.md`:
- `## UX/UI` → `- [ ] Mockup: ux-ui/` (describes what mockups should show)

### ux-ui.md §User Flows
Feeds `spec.md`:
- `### Happy Path` acceptance criteria (multi-step flows become given/when/then)

Feeds `test_plan.md`:
- `## Integration / UI` → `- [ ] **Full flow**: [end-to-end steps]`

---

## supplementary.md → MEMORY.md + takeaways.md

### supplementary.md (all sections)
Feeds `MEMORY.md`:
- Background context, stakeholder notes, organizational knowledge
- This file preserves information that may be relevant across features

Feeds `takeaways.md`:
- After the feature ships, supplementary content may yield lessons for
  `## What We Learned` or `## API / Tech Surprises`

---

## gaps.md → All Templates

### gaps.md each section
Each unanswered gap blocks one or more SDD template fields from being
filled correctly. The downstream agent should not proceed with a template
field that has an unresolved gap in its corresponding knowledge section.

- **Blocking spec.md** → user story, acceptance criteria, requirements gaps
- **Blocking plan.md** → tech context, approach, dependency, risk gaps
- **Blocking tasks.md** → implementation order, file structure gaps
- **Blocking test_plan.md** → test scenario, edge case gaps

---

## index.md → spec plan coordination

### index.md
Read by the SDD coordinator agent (or the human) to understand:
- Which knowledge files exist and what they contain
- Which SDD templates are ready to fill vs. blocked by gaps
- The overall extraction quality (inferred items vs. extracted items)
