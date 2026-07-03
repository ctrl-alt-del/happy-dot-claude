# Migration Guide

## Schema Versioning

All JSON files in `memory/` carry a schema version field. The skill's SKILL.md
carries a matching version in its frontmatter.

| File | Version field |
|---|---|
| `memory/meta.json` | `"version": "1.0.0"` |
| `memory/graph.json` | `"version": "1.0.0"` |

## Version History

| Version | Date | Changes |
|---|---|---|
| `1.0.0` | 2026-07-03 | Initial schema |

## Onboarding Scenarios

### Scenario 1: Fresh project (no MEMORY.md, no `memory/`)

```bash
scripts/memory-init.sh
```

What happens:
1. Creates a template MEMORY.md with section headers and empty entries.
2. Creates `memory/` directory structure.
3. Writes `memory/meta.json` with `version: "1.0.0"` and empty entries array.
4. Writes `memory/graph.json` with `version: "1.0.0"`, empty nodes/edges.
5. Creates `memory/raw/` directory.
6. Adds `memory/raw/` and `memory/.backup/` to `.gitignore`.
7. Reports: "Memory scaffolded. Run memory-collect.sh to start observing."

### Scenario 2: Plain MEMORY.md (no frontmatter, no `memory/`)

```bash
scripts/memory-init.sh
```

What happens:
1. Detects existing MEMORY.md without `memory/meta.json` alongside.
2. Backs up MEMORY.md to `memory/.backup/YYYY-MM-DD--pre-migration/MEMORY.md`.
3. Parses MEMORY.md into entries:
   - Sections (`## 🧠 Tech Gotchas`, `## 🔧 Patterns That Worked`, etc.) become entry boundaries.
   - Each entry gets an auto-assigned `mem-XXX` ID.
   - Entry `type` is inferred from section: Gotchas → `gotcha`, Patterns → `pattern`, Decisions → `decision`, Facts → `fact`, Bugs → `gotcha`.
   - Entries with `⚡` marker get `pinned: true` and `confidence: 0.9`.
   - Tags are inferred from any `#tag` mentions in the entry body.
4. Rewrites MEMORY.md with YAML frontmatter blocks prepended to each entry.
5. Creates `memory/` directory structure with extracted metadata.
6. Builds initial `memory/graph.json` from `related` fields and tag overlap.
7. Adds gitignore entries.
8. Reports: "Parsed N entries from existing MEMORY.md. Enriched with metadata."

### Scenario 3: Existing `memory/` directory (may need migration)

```bash
scripts/memory-migrate.sh
```

What happens:
1. Reads `memory/meta.json` to determine current version.
2. Compares to target version (from skill SKILL.md frontmatter).
3. If versions match: "Already at latest version. Nothing to migrate."
4. If older: determine migration chain (v1.0 → v1.1 → v1.2 → ...).
5. For each step in chain, execute migration function.

## Migration Chain

Migration uses a strict chain: no direct jumps from v1.0 to v1.3.
Each version ships a `migrate_from_v<old>_to_v<new>()` function.

### Future migration structure (template)

When adding schema v1.1.0:

```
scripts/memory-migrate.sh:
  - Add "1.1.0" to KNOWN_VERSIONS array
  - Add migrate_1_0_0_to_1_1_0() function
```

## Migration Safety Protocol

Every `memory-migrate.sh` run follows this sequence:

1. **Pre-flight validation**
   - Schema check: all required fields present in meta.json and graph.json.
   - Referential integrity: all `related` IDs exist in entries.
   - File integrity: check `MANIFEST.sha256` of most recent snapshot.

2. **Backup**
   - Copy all of `memory/` to `memory/.backup/<timestamp>--v<old>/`.
   - Compute and write `MANIFEST.sha256` for the backup.
   - Update `memory/.backup/manifest.json` with new snapshot entry.
   - Set `latest` symlink to new backup.

3. **Migration**
   - Apply transformations to temp files (not in-place).
   - Validate each migration step's output before continuing.

4. **Post-migration validation**
   - Schema check on migrated files.
   - Referential integrity check.
   - Entry count preserved (unless migration explicitly removes entries,
     in which case a tombstone is created).

5. **Atomic apply**
   - Rename temp files to real files (atomic on same filesystem).
   - Update version fields.

6. **Report**
   - Print: "Migrated from vX.Y.Z to vA.B.C. Preserved N entries, enhanced M,
     deprecated K."

### Failure handling

If any step fails:
- Temp files are deleted.
- Backup is intact.
- Error message: "Migration failed at step [X]. Backup available at
  memory/.backup/<timestamp>--v<old>/. Aborting. Restore with:
  cp -r memory/.backup/<timestamp>--v<old>/* memory/"

### Dry-run

```bash
scripts/memory-migrate.sh --dry-run
```

Runs validation and migration to temp files but does not apply. Reports what
would change without modifying anything.

## Rollback

Beyond migration, `memory-evolve.sh` creates snapshots before every evolution
run. If an evolution cycle produces undesirable results:

```bash
scripts/memory-evolve.sh --rollback <hash>
```

This restores `memory/meta.json`, `memory/graph.json`, and `memory/raw/` from
the specified snapshot in `.backup/`. MEMORY.md is NOT rolled back (it is the
human-editable source and may have been edited since the snapshot).

## Snapshot Retention

`memory/.backup/manifest.json` tracks all snapshots:

```json
{
  "snapshots": [
    {"id": "a3f2b1c9", "created": "...", "version": "1.0.0", "evolution_id": "ev-004"},
    {"id": "f9e4d7a2", "created": "...", "version": "1.0.0", "evolution_id": "ev-005"}
  ],
  "retention": {"max_snapshots": 7, "min_age_days": 0}
}
```

Garbage collection during evolved runs:
- Keep last 7 snapshots by creation time.
- Keep at least 1 snapshot per schema version (for migration compatibility).
- Deduplicate identical hashes (keep oldest copy).
