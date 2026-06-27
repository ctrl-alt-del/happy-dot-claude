#!/usr/bin/env bash
set -euo pipefail

# install.sh — symlink each skill in this repo into ~/.claude/skills/<skill-name>.
#
# A "skill" is any top-level directory containing a SKILL.md file.
# Existing real directories/files are never clobbered. Stale symlinks that point
# elsewhere are only replaced when --force is given.
#
# Usage: ./install.sh [--dry-run] [--force]

DRY_RUN=0
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --force)   FORCE=1 ;;
    -h|--help)
      echo "Usage: ./install.sh [--dry-run] [--force]"
      echo
      echo "Symlinks each skill (a top-level dir with a SKILL.md) into ~/.claude/skills."
      echo "  --dry-run  Show what would happen without making changes."
      echo "  --force    Replace existing symlinks that point elsewhere."
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: ./install.sh [--dry-run] [--force]" >&2
      exit 2
      ;;
  esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

if [ ! -d "$SKILLS_DIR" ]; then
  echo "Creating $SKILLS_DIR"
  run mkdir -p "$SKILLS_DIR"
fi

linked=0
skipped=0

for skill_md in "$REPO_DIR"/*/SKILL.md; do
  [ -e "$skill_md" ] || continue
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  dest="$SKILLS_DIR/$name"

  if [ -L "$dest" ]; then
    current="$(readlink "$dest")"
    if [ "$current" = "$src" ]; then
      echo "= $name (already linked)"
      skipped=$((skipped + 1))
      continue
    fi
    if [ "$FORCE" -eq 1 ]; then
      echo "~ $name (replacing stale symlink -> $current)"
      run rm "$dest"
    else
      echo "! $name skipped: symlink points elsewhere ($current). Use --force to replace."
      skipped=$((skipped + 1))
      continue
    fi
  elif [ -e "$dest" ]; then
    echo "! $name skipped: a real directory/file already exists at $dest (not touching it)."
    skipped=$((skipped + 1))
    continue
  fi

  echo "+ $name -> $dest"
  run ln -s "$src" "$dest"
  linked=$((linked + 1))
done

echo
summary="Done. Linked: $linked, skipped: $skipped."
if [ "$DRY_RUN" -eq 1 ]; then
  summary="$summary (dry-run, no changes made)"
fi
echo "$summary"
