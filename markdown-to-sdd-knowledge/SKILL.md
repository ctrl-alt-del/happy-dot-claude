---
name: markdown-to-sdd-knowledge
description: >
  Convert markdown documents (feature requests, PRDs, meeting notes, bug reports,
  Slack threads, technical briefs, or any unstructured markdown describing a feature
  or change) into structured, atomic knowledge files for Spec-Driven Development
  workflows. Use this skill whenever the user provides markdown content describing
  a feature, change, or requirement and needs structured knowledge extracted for
  generating SDD artifacts like plan.md and spec.md. Also trigger when the user
  mentions "extracting requirements," "converting docs to specs," "structuring
  features," "knowledge extraction for SDD," "turn this into a spec," or when they
  paste a document and ask to prepare it for downstream AI agents.
---

# Markdown to SDD Knowledge Extractor

## Purpose

Transform arbitrary markdown documents into a structured, multi-file knowledge
representation that downstream SDD agents can consume to generate `spec.md`,
`plan.md`, `tasks.md`, and `test_plan.md`.

The knowledge files are the bridge between raw input and SDD artifacts. They
separate the work of "what does the source actually say?" from "how do we fill
in these templates?" — so that template-filling agents don't need to reread
the original and risk fabricating content.

## When to Trigger

- User shares a markdown file or pastes markdown content and asks to
  extract requirements, prepare it for SDD, or structure it for agents
- User says "turn this into a spec," "extract the knowledge," or
  "convert this doc into structured format"
- User provides a PRD, feature request, bug report, meeting notes, or
  technical brief describing a feature or change
- User mentions "knowledge extraction," "SDD preprocessing," or
  "feed this into the SDD workflow"

## Workflow

### Step 1: Read and Understand

Read the entire input markdown. Before extracting, build a mental map:
- What is the primary change or feature being described?
- What kind of document is this (PRD, bug report, meeting notes, Slack thread)?
- What domain is it in (mobile app, API, CLI, web)?
- Where is the information dense vs. thin?

### Step 2: Extract into Knowledge Files

Produce the output structure defined below. Work through the source
systematically, placing every fact, constraint, and nuance into the
appropriate file.

**Extraction rules follow in the "Extraction Principles" section.**
Read them before you begin extracting — they're essential to getting
this right.

### Step 3: Present and Validate

After writing the knowledge files:

1. Show the user `index.md` — it summarizes what was extracted and flags gaps
2. Walk through each `[INFERRED]` or `[SYNTHESIZED]` item and ask for
   confirmation or correction
3. Walk through `gaps.md` — each gap is a concrete question. Ask the user
   to answer or explicitly mark it as out of scope
4. Update files based on user feedback

Do not proceed to downstream SDD steps (generating spec.md, plan.md, etc.)
until the user has validated the knowledge files.

## Output Structure

Create a `knowledge/` directory containing these files:

```
knowledge/
├── index.md           # ALWAYS — entry point and summary
├── requirements.md    # ALWAYS — user story, functional/non-functional reqs, acceptance criteria
├── approach.md        # ALWAYS — technical context, dependencies, risks, file paths
├── ux-ui.md           # CONDITIONAL — only if source mentions UI, UX, or visual elements
├── gaps.md            # ALWAYS — what's missing for SDD completeness
└── supplementary.md   # ALWAYS — everything else from the source
```

**Never create `ux-ui.md` if the source has zero UI/UX content.**
Creating empty files that imply non-existent content is a form of
fabrication. Instead, note in `gaps.md` if UI/UX is relevant but missing.

### index.md

```markdown
# Knowledge Extraction — Index

## Source
- **Source**: [filename, URL, or "user prompt"]
- **Extracted**: [timestamp]
- **Project**: [project name if known, else "unspecified"]

## Summary
[One paragraph: what feature or change this is about, in your own words
but based strictly on the source. Tag as [SYNTHESIZED] if combining
multiple source statements.]

## File Inventory

| File | Purpose | Feeds SDD Template |
|------|---------|--------------------|
| requirements.md | User story, functional/non-functional reqs, acceptance criteria | spec.md, test_plan.md |
| approach.md | Technical context, dependencies, risks, file paths | plan.md, tasks.md |
| ux-ui.md | UI/UX descriptions from source | spec.md |
| supplementary.md | All other source content not fitting above categories | MEMORY.md, takeaways.md |
| gaps.md | What's missing — questions for the user | All templates |

## Extraction Stats
- **Total source facts captured**: [count]
- **Inferred items**: [count — needs user confirmation]
- **Gaps**: [count — needs user answers]
- **Source coverage**: [rough % — how much of the source content landed in structured files vs. supplementary]
```

### requirements.md

```markdown
# Requirements

## Problem Statement
[What problem does this solve? Extract or quote from source.]
[Tag: [EXTRACTED] if verbatim, [SYNTHESIZED] if combining source statements.]

## User Story
[Who wants what and why. Extract from source.]
[Tag: [EXTRACTED] if in source, [INFERRED] if reasoned from context.]

## Functional Requirements
[Numbered list. Each item must be a testable statement.]
[Source citation after each item.]

Format:
1. [Requirement]
   → Source: §[section], "[direct quote or paraphrase]"
2. [Requirement]
   → Source: line [N], "[direct quote or paraphrase]"

## Non-Functional Requirements
[Performance, security, accessibility, offline, compatibility, etc.]
[Source citation for each. Leave section empty if none in source.]

## Acceptance Criteria

### Happy Path
[Given/when/then statements from source.]
[Source citation for each. If none in source, write "Not specified in source."]

### Edge Cases / Error Handling
[Error conditions, boundary cases, fallback behavior from source.]
[Source citation for each. If none, write "Not specified in source."]
```

### approach.md

```markdown
# Technical Approach

## Tech Context
[Languages, frameworks, APIs, libraries, patterns mentioned in the source.]
[Source citation for each. If nothing technical is mentioned, write
"Not specified in source."]

## Files Referenced
[File paths or file types mentioned in the source — what code might be
created, modified, or touched.]
[Source citation for each. If none, write "Not specified in source."]

## Dependencies
[What this feature depends on: other features, services, APIs, libraries,
teams, external systems.]
[Source citation for each.]

## Risks
[Risks, edge cases, concerns, or caveats mentioned in the source.]
[Source citation for each. Tag [INFERRED] if deduced from context.]

## Constraints
[Deadlines, resource limits, compatibility requirements, "must not break X"
type constraints from source.]
[Source citation for each.]
```

### ux-ui.md

Only create this file if the source describes UI elements, screens,
interactions, visual design, mockups, or user flows. If created:

```markdown
# UX/UI

## Screens / Views
[What screens or views are described. Source citation for each.]

## Interactions
[User interactions described: taps, swipes, navigation, gestures.
Source citation for each.]

## Visual Details
[Colors, layouts, spacing, typography, icons mentioned.
Source citation for each.]

## User Flows
[Multi-step flows or sequences described. Source citation for each.]
```

### gaps.md

```markdown
# Gaps — Information Needed

[For each gap, write a concrete question the user can answer. Group by
which SDD template it blocks.]

## Blocking spec.md
- [ ] [Question about user story, acceptance criteria, or requirements]

## Blocking plan.md
- [ ] [Question about tech stack, approach, dependencies, or risks]

## Blocking tasks.md
- [ ] [Question about implementation order or file structure]

## Blocking test_plan.md
- [ ] [Question about test scenarios or edge cases]
```

Each gap must be:
- A concrete, answerable question (not "More detail needed")
- Linked to the SDD template it blocks (so the user knows why it matters)
- Only included if the missing information is actually needed for the SDD
  workflow. If a topic is genuinely out of scope, note that instead.

### supplementary.md

**Purpose**: This is the safety net. Every piece of information in the
source that doesn't fit cleanly into `requirements.md`, `approach.md`, or
`ux-ui.md` goes here. This ensures no information is lost.

```markdown
# Supplementary Information

[Content from the source that doesn't fit the structured categories above,
organized by topic. Each section includes source citations.]

## [Topic 1]
[Content with source citation.]

## [Topic 2]
[Content with source citation.]
```

This file preserves context, background, stakeholder notes, and other
information that downstream agents might need for context but that doesn't
directly fill an SDD template field.

## Extraction Principles

These five principles govern every extraction. Violating any of them
produces knowledge that cannot be trusted by downstream agents.

### Principle 1: Fidelity over Completeness

A `knowledge/` directory with gaps is better than one with fabricated
content. Downstream agents will make implementation decisions based on
these files — wrong information causes more damage than missing
information.

If the source says "the button should be blue" and you write "the button
should be blue (primary brand color)," you've fabricated. The source
didn't say it's the brand color.

### Principle 2: Preserve Everything

No sentence, fact, constraint, aside, or nuance from the source is
discarded. Every piece of information lands in one of the output files.

If something doesn't fit `requirements.md`, `approach.md`, or `ux-ui.md`,
it goes into `supplementary.md`. That file is organized by topic, not a
dump — but its purpose is completeness.

Before finalizing, do a pass: "Did I capture everything the source says?"
If the source is 500 words, your knowledge files should account for all
500 words' worth of information.

### Principle 3: Always Cite

Every fact in the output must be traceable to the source. Use inline
citations consistently:

- `→ Source: §Problem Statement, "The login flow must support SSO"`
- `→ Source: line 23-25, "We need to handle network errors gracefully"`
- `→ Source: Slack thread, Alice: "auth should use OAuth2 not basic"`

Citations serve two purposes: they let the user verify accuracy, and they
let downstream agents understand the provenance of each claim.

### Principle 4: Tag Inference Explicitly

Use these tags consistently to distinguish what the source says from
what you reason:

- **No tag** = directly extracted from source (paraphrased is fine if
  meaning is preserved)
- **`[INFERRED]`** = reasoned from context but not explicitly stated.
  Example: source says "the API returns 401 when the token expires" →
  you infer "the client must handle token refresh" — tag this [INFERRED].
- **`[SYNTHESIZED]`** = combining multiple source statements into one
  summary. Example: three paragraphs about latency, one about volume →
  you synthesize "the system must handle 10K req/s with p99 < 100ms."

[INFERRED] and [SYNTHESIZED] items MUST be reviewed by the user before
downstream agents consume them.

### Principle 5: Handle Ambiguity by Surfacing It

When the source is ambiguous, present both interpretations and ask.

Bad: silently pick one → "The user must enter a username"
Good: "The source says 'login with credentials' (line 5). This could
mean username+password, email+password, or SSO. Which is intended?"

Ambiguity is valuable information — it tells the user their source doc
needs clarification. Don't resolve it by guessing.

## What NOT to Do

- **Don't add requirements.** If the source says "login screen" and you
  add "with remember-me checkbox," you're fabricating.
- **Don't guess tech stack.** If the source doesn't mention a language or
  framework, leave it as "Not specified in source." Don't assume React
  just because the project uses React elsewhere.
- **Don't fill in acceptance criteria.** If the source says "users should
  be able to reset their password" but doesn't specify error cases, write
  "Not specified in source" — don't invent "invalid email shows error."
- **Don't create empty files.** If there's no UI content, don't create
  `ux-ui.md`. An empty file implies content exists but you chose not to
  write it.
- **Don't discard context.** Meeting notes might contain "Jim from backend
  says the API is behind by 2 weeks." This doesn't fit any SDD template,
  but it's critical context for planning. It goes in `supplementary.md`.

## References

- `references/sdd-fields.md` — Maps each section of each knowledge file
  to the specific SDD template fields they feed. Read this when you need
  to understand how downstream agents will consume the knowledge.
