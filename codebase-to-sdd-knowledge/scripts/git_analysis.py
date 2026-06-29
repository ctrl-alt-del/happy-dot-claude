#!/usr/bin/env python3
"""Analyze git history for hotspots, ownership, and reverted commits.

Usage:
    python git_analysis.py /path/to/project

Output: JSON to stdout with keys:
    hotspots, owners, reverted_commits, bug_patterns
"""

import json
import os
import subprocess
import sys
from collections import Counter


def run_git(root, args):
    try:
        result = subprocess.run(
            ["git", "-C", root] + args,
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return ""


def get_hotspots(root, limit=20):
    """Get most frequently changed files from git log."""
    output = run_git(root, [
        "log", "--format=", "--name-only", "--diff-filter=M",
        "-n", "500", "--", "."
    ])
    if not output:
        return []

    file_counts = Counter()
    for line in output.split("\n"):
        line = line.strip()
        if line:
            file_counts[line] += 1

    top = file_counts.most_common(limit)
    return [{"file": f, "changes": c} for f, c in top]


def get_owners(root, limit=15):
    """Get directory-level ownership from git blame aggregation."""
    # Get list of tracked files
    output = run_git(root, ["ls-files"])
    if not output:
        return []

    files = [f for f in output.split("\n") if f.strip()]

    dir_owners = {}

    for f in files:
        dirname = os.path.dirname(f) or "."
        if not dirname.startswith(".") and dirname != ".":
            dirname = dirname.split("/")[0]

        blame_output = run_git(
            root,
            ["log", "--format=%an", "--follow", "-n", "5", "--", f]
        )
        if blame_output:
            authors = [a for a in blame_output.split("\n") if a.strip()]
            if authors:
                top_author = Counter(authors).most_common(1)[0][0]
                if dirname not in dir_owners:
                    dir_owners[dirname] = Counter()
                dir_owners[dirname][top_author] += 1

    result = []
    for d, counter in sorted(dir_owners.items(),
                              key=lambda x: sum(x[1].values()), reverse=True):
        total = sum(counter.values())
        authors = counter.most_common(2)
        primary = authors[0] if len(authors) > 0 else ("unknown", 0)
        secondary = authors[1] if len(authors) > 1 else (None, 0)

        entry = {
            "directory": d,
            "total_files": total,
            "primary_owner": primary[0],
            "primary_pct": round(primary[1] / total * 100, 1)
        }
        if secondary[0]:
            entry["secondary_owner"] = secondary[0]
            entry["secondary_pct"] = round(secondary[1] / total * 100, 1)

        result.append(entry)
        if len(result) >= limit:
            break

    return result


def get_reverted_commits(root, limit=10):
    """Find reverted commits — signals past bugs and unstable areas."""
    output = run_git(root, [
        "log", "--format=%H|%s|%an|%ad",
        "--date=short", "-n", "200", "--grep=Revert",
        "--", "."
    ])
    if not output:
        return []

    reverts = []
    for line in output.split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, subject, author, date = parts

        # Get the files affected by this revert
        files = run_git(root, ["diff-tree", "--no-commit-id",
                                "--name-only", "-r", commit_hash])
        affected_files = [f for f in files.split("\n") if f.strip()]

        reverts.append({
            "commit": commit_hash[:8],
            "message": subject,
            "author": author,
            "date": date,
            "files": affected_files[:10],
        })

        if len(reverts) >= limit:
            break

    return reverts


def get_bug_patterns(reverted_commits):
    """Identify files and directories frequently involved in reverts."""
    file_counter = Counter()
    for rc in reverted_commits:
        for f in rc.get("files", []):
            file_counter[f] += 1

    dir_counter = Counter()
    for f, c in file_counter.most_common():
        d = os.path.dirname(f) or "."
        if d != ".":
            d = d.split("/")[0]
            dir_counter[d] += c

    return {
        "hotspot_files": [
            {"file": f, "revert_count": c}
            for f, c in file_counter.most_common(10)
        ],
        "hotspot_directories": [
            {"directory": d, "revert_count": c}
            for d, c in dir_counter.most_common(5)
        ],
    }


def get_commit_style(root):
    """Infer commit message conventions from recent commits."""
    output = run_git(root, [
        "log", "--format=%s", "-n", "50"
    ])
    if not output:
        return {"convention": "unknown"}

    subjects = [l.strip() for l in output.split("\n") if l.strip()]
    conventional_count = 0
    prefixes = Counter()

    for s in subjects:
        if ":" in s and " " in s:
            parts = s.split(":", 1)
            if len(parts) == 2:
                prefix = parts[0].strip()
                if " " not in prefix and not prefix[0].isdigit():
                    prefixes[prefix] += 1
                    conventional_count += 1

    if conventional_count > len(subjects) * 0.6:
        convention = "conventional-commits"
        top_prefixes = prefixes.most_common(5)
    elif conventional_count > len(subjects) * 0.3:
        convention = "semi-conventional"
        top_prefixes = prefixes.most_common(5)
    else:
        convention = "free-form"
        top_prefixes = []

    return {
        "convention": convention,
        "sample_size": len(subjects),
        "conventional_pct": round(conventional_count / len(subjects) * 100, 1),
        "common_prefixes": [p[0] for p in top_prefixes],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python git_analysis.py /path/to/project", file=sys.stderr)
        sys.exit(1)

    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(root, ".git")):
        print(json.dumps({
            "error": "Not a git repository (no .git directory found)",
            "hotspots": [],
            "owners": [],
            "reverted_commits": [],
            "bug_patterns": {},
            "commit_style": {"convention": "unknown"},
        }, indent=2))
        return

    hotspots = get_hotspots(root)
    owners = get_owners(root)
    reverted = get_reverted_commits(root)
    bug_patterns = get_bug_patterns(reverted)
    commit_style = get_commit_style(root)

    result = {
        "hotspots": hotspots,
        "owners": owners,
        "reverted_commits": reverted,
        "bug_patterns": bug_patterns,
        "commit_style": commit_style,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
