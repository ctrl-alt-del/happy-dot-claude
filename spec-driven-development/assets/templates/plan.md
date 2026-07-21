---
feature_id: "NNN"
name: "Feature Name"
status: "🚧 In Progress"
depends_on: []
touches:
  - "FileA.ext"
  - "FileB.ext"
created: "YYYY-MM-DD"
---

# [Feature Name] — Implementation Plan

<!--
  INSTRUCTIONS FOR AI:
  - Fill every section. Use [NEEDS CLARIFICATION: ...] for unknown details.
  - Run the Constitution Check gates FIRST. If any gate fails, document in
    Complexity Tracking with justification.
  - Keep the main document high-level. Extract lengthy code samples, detailed
    algorithms, or schema definitions to the relevant section or reference
    files.
  - Delete this comment block when done.
-->

## Technical Context

**Language/Version**: [e.g., TypeScript 5.4, Python 3.12, Rust 1.78 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., React 18, FastAPI, LLVM or NEEDS CLARIFICATION]
**Storage**: [e.g., PostgreSQL, SQLite, files, or N/A]
**Testing**: [e.g., Jest, pytest, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, browser or NEEDS CLARIFICATION]
**Performance Goals**: [e.g., 1000 req/s, 60 fps, <200ms p95 or NEEDS CLARIFICATION]
**Constraints**: [e.g., <100MB memory, offline-capable, no external APIs or NEEDS CLARIFICATION]
**Scale/Scope**: [e.g., 10k users, 1M records, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before implementation. Re-check after design changes.*

- [ ] **Article I (Spec-First)**: spec.md approved by stakeholder?
- [ ] **Article II (Test-First)**: test plan written before implementation code?
- [ ] **Article III (Modularity)**: feature is a self-contained module with clear boundaries?
- [ ] **Article IV (Simplicity)**: ≤3 new files? No speculative features? No future-proofing?
- [ ] **Article V (Anti-Abstraction)**: using framework directly? No unnecessary wrappers?
- [ ] **Article VI (Integration Reality)**: contract tests defined? Real components over mocks?
- [ ] **Article VII (Observability)**: health checks, structured logs, and metrics planned?

## Approach

[High-level strategy. What's the main design idea? How does it fit into the existing architecture?]

## Data Model

<!-- Entities, their key attributes, and relationships. No DDL or code — describe at design level. -->

| Entity | Key Attributes | Relationships |
|--------|---------------|---------------|
| [Entity1] | [attr1, attr2, attr3] | belongs to [Entity2] |
| [Entity2] | [attr1, attr2] | has many [Entity1] |

## API / CLI Contract

<!-- For API projects: list endpoints, methods, request/response shapes. For CLI: list commands, flags, input/output formats. Keep high-level — not full OpenAPI spec. -->

| Method | Path / Command | Purpose | Input | Output |
|--------|---------------|---------|-------|--------|
| GET | /api/items | List items | query params | Item[] |
| POST | /api/items | Create item | Item body | Item |

## Alternatives Considered

<!-- One of the MOST IMPORTANT sections. Document what you considered and WHY you chose this approach. -->

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| [Alternative A] | [advantages] | [disadvantages] | [reason] |
| [Alternative B] | [advantages] | [disadvantages] | [reason] |

**Decision**: [Which approach was chosen and why the trade-offs are acceptable]

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk description] | Low/Med/High | Low/Med/High | [How we mitigate] |

## Dependencies

| Depends On | Status | Blocking? |
|-----------|--------|-----------|
| [Feature, API, library, or team] | Ready/In Progress/Blocked | Yes/No |

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Article | Violation | Why Needed | Simpler Alternative Rejected Because |
|---------|-----------|------------|--------------------------------------|
| Art. IV | 5 new files | [justification] | [why simpler approach doesn't work] |

## Files to Create / Change

| Action | File | Rationale |
|--------|------|-----------|
| Create | src/models/entity.py | New data model |
| Modify | src/api/routes.py | Add new endpoint |

## Quickstart Validation

<!-- Key scenarios to verify the feature works end-to-end after implementation -->
1. [Validation scenario 1 — step by step]
2. [Validation scenario 2 — step by step]
