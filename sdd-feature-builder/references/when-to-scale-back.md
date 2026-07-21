# When to Scale Back the SDD Workflow

Not every change needs the full SDD workflow. Apply judgment.

## Skip the Full Workflow When

### Trivial Changes (no spec needed)
- Typo fixes, comment corrections, whitespace changes
- Adding a single log line
- Updating a dependency version (patch)
- Renaming a variable/function with no behavioral change
- Config value change (single line)

→ Just implement directly with verification.

### Small, Unambiguous Changes (lightweight spec)
- Adding a single, well-defined endpoint to an existing pattern
- Fixing a bug with a known root cause
- Adding a field to an existing model (follow existing pattern)
- Simple formatting/lint fixes

→ Write a 1-paragraph spec in the commit message or a brief issue comment.
  Skip plan.md, skip test_plan.md, skip mockups. Write tasks as a short
  checklist. Still run build+test+lint per task.

### When a Prototype is More Valuable Than a Spec
- Exploring a novel algorithm where you don't know what's possible
- UI experiments where visual iteration is faster than written description
- Spike solutions to understand a new library or API

→ Say explicitly: "This is a prototype. No spec." Write a quick README
  in the branch with what you're exploring. The spec comes after the
  prototype validates the approach.

## Never Skip

Even for trivial changes, never skip:
- Build + test + lint verification
- Reading MEMORY.md for relevant gotchas
- Updating index.md if file touches change
- Checking constitution.md for applicable gates

## Decision Flow

```
Change requested
│
├── Is it a typo, log line, config value, or rename?
│   └── YES → Implement directly. Verify build+test+lint. Done.
│
├── Is it a single, well-defined addition following an existing pattern?
│   └── YES → Write brief spec. Skip plan. Lightweight tasks. Done.
│
├── Is it exploratory / you don't know what's possible yet?
│   └── YES → Prototype explicitly. Spec comes later if it works.
│
└── NO → Full SDD workflow: constitution → spec → clarify → plan →
         checklist → tasks → analyze → implement → converge → ship
```
