#!/usr/bin/env python3
"""Generate an annotated directory tree with optional tree-sitter symbol extraction.

Usage:
    python structure_map.py /path/to/project

Output: annotated directory tree to stdout with:
    - File type classification (source, test, config, doc, generated)
    - Optional symbol extraction (if tree-sitter is available)
"""

import json
import os
import subprocess
import sys


EXCLUDE_DIRS = {
    ".git", "node_modules", "vendor", "target", "__pycache__",
    ".venv", "venv", ".tox", "dist", "build", ".next", ".turbo",
    "coverage", ".nyc_output", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "bower_components", ".terraform",
}

GENERATED_PATTERNS = [
    ".gen.", ".generated.", "-gen.", ".pb.", ".pb.go",
    ".g.dart", ".freezed.dart", ".grpc.",
    "_string.go", "_mock.go",
]

SOURCE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".pyi",
    ".go",
    ".rs",
    ".java", ".kt", ".kts",
    ".rb", ".rake",
    ".ex", ".exs", ".eex", ".heex",
    ".php",
    ".swift",
    ".dart",
    ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
    ".scala", ".sc",
    ".r", ".R",
    ".lua",
    ".zig",
    ".nim",
    ".ml", ".mli",
    ".hs",
    ".elm",
    ".clj", ".cljs", ".cljc", ".edn",
    ".fs", ".fsx", ".fsi",
    ".erl", ".hrl",
    ".sql", ".psql",
    ".vue", ".svelte",
    ".graphql", ".gql",
    ".proto",
    ".prisma",
    ".yaml", ".yml",
    ".json",
    ".toml",
    ".md", ".mdx",
}

TEST_EXTENSIONS = {".test.", ".spec.", "_test.", "_spec."}

CONFIG_NAMES = {
    "package.json", "tsconfig.json", "pyproject.toml", "Cargo.toml",
    "go.mod", "Makefile", "Dockerfile", "docker-compose.yml",
    ".env", ".env.example", ".env.template",
    ".eslintrc", ".prettierrc", "eslint.config",
    ".gitignore", ".gitattributes",
}


def classify_file(filepath):
    """Classify a file as source, test, config, doc, or generated."""
    basename = os.path.basename(filepath)
    _, ext = os.path.splitext(basename)

    if basename in CONFIG_NAMES or basename.startswith(".env"):
        return "config"

    if ext == ".md" or ext == ".mdx":
        return "doc"

    for pattern in GENERATED_PATTERNS:
        if pattern in basename:
            return "generated"

    for pattern in TEST_EXTENSIONS:
        if pattern in basename:
            return "test"

    if ext in SOURCE_EXTENSIONS:
        return "source"

    if ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
               ".woff", ".woff2", ".ttf", ".eot", ".otf"):
        return "asset"

    return "other"


def trim_tree(tree, max_depth=5, max_children=30):
    """Limit tree depth and breadth for readability."""
    def _trim(node, depth):
        if depth > max_depth:
            return {"name": node["name"], "type": "directory",
                    "children": [{"name": "...", "type": "ellipsis"}]}
        if "children" not in node:
            return node
        children = node["children"][:max_children]
        result = dict(node)
        result["children"] = [_trim(c, depth + 1) for c in children]
        if len(node["children"]) > max_children:
            result["children"].append(
                {"name": f"... ({len(node['children']) - max_children} more)",
                 "type": "ellipsis"}
            )
        return result
    return _trim(tree, 0)


def build_tree(root_path, rel_path="", depth=0, max_depth=6):
    """Build a nested directory tree structure."""
    full_path = os.path.join(root_path, rel_path) if rel_path else root_path
    name = os.path.basename(full_path) if rel_path else "."

    if depth >= max_depth:
        return {"name": name, "type": "directory",
                "children": [{"name": "...", "type": "ellipsis"}]}

    try:
        entries = sorted(os.listdir(full_path))
    except PermissionError:
        return {"name": name, "type": "directory", "error": "permission_denied"}

    children = []
    for entry in entries:
        if entry.startswith(".") and entry not in {".github", ".env.example",
                                                     ".env.template"}:
            continue
        if entry in EXCLUDE_DIRS:
            continue

        entry_path = os.path.join(full_path, entry)
        entry_rel = os.path.join(rel_path, entry) if rel_path else entry

        if os.path.isdir(entry_path):
            subtree = build_tree(root_path, entry_rel, depth + 1, max_depth)
            children.append(subtree)
        else:
            file_type = classify_file(entry)
            children.append({
                "name": entry,
                "type": file_type,
            })

    return {
        "name": name,
        "type": "directory",
        "children": children,
    }


def count_by_type(tree, counter=None):
    """Count files by type in the tree."""
    if counter is None:
        counter = {}

    if "children" not in tree:
        return counter

    for child in tree["children"]:
        if child.get("type") == "directory":
            count_by_type(child, counter)
        elif child.get("type") not in ("ellipsis", None):
            t = child["type"]
            counter[t] = counter.get(t, 0) + 1

    return counter


def extract_symbols(root_path, rel_path):
    """Try to extract symbols from a source file using available tools."""
    full_path = os.path.join(root_path, rel_path)
    _, ext = os.path.splitext(rel_path)
    symbols = []

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Function definitions (common across languages)
            if "fn " in stripped and ("pub " in stripped or "fn " == stripped[:3]):
                symbols.append({"line": i + 1, "kind": "function",
                                "text": stripped[:120]})
            elif stripped.startswith("def ") and "(" in stripped:
                symbols.append({"line": i + 1, "kind": "function",
                                "text": stripped[:120]})
            elif stripped.startswith("func ") and "(" in stripped:
                symbols.append({"line": i + 1, "kind": "function",
                                "text": stripped[:120]})

            # Class / struct / interface definitions
            if any(stripped.startswith(p) for p in
                   ["class ", "struct ", "enum ", "interface ", "type ",
                    "trait ", "impl "]):
                symbols.append({"line": i + 1, "kind": "type",
                                "text": stripped[:120]})

            # Exports
            if stripped.startswith("export ") and not stripped.startswith("export default"):
                symbols.append({"line": i + 1, "kind": "export",
                                "text": stripped[:120]})

    except (IOError, UnicodeDecodeError, PermissionError):
        pass

    return symbols[:20]  # limit per file


def main():
    if len(sys.argv) < 2:
        print("Usage: python structure_map.py /path/to/project", file=sys.stderr)
        sys.exit(1)

    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    tree = build_tree(root)
    counts = count_by_type(tree)

    # Collect top-level directory information
    top_dirs = []
    try:
        for entry in sorted(os.listdir(root)):
            if entry.startswith(".") and entry != ".github":
                continue
            entry_path = os.path.join(root, entry)
            if os.path.isdir(entry_path) and entry not in EXCLUDE_DIRS:
                # Count source files in this directory
                src_count = 0
                test_count = 0
                for dirpath, dirnames, filenames in os.walk(entry_path):
                    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS
                                   and not d.startswith(".")]
                    for f in filenames:
                        ft = classify_file(os.path.join(dirpath, f))
                        if ft == "source":
                            src_count += 1
                        elif ft == "test":
                            test_count += 1
                    if src_count > 100:
                        break

                desc = []
                if src_count > 0:
                    desc.append(f"{src_count} source files")
                if test_count > 0:
                    desc.append(f"{test_count} test files")
                if not desc:
                    desc.append("no source files")

                top_dirs.append({
                    "name": entry,
                    "description": ", ".join(desc),
                })
    except PermissionError:
        pass

    result = {
        "project_root": root,
        "file_counts": counts,
        "top_level_directories": top_dirs,
        "tree": tree,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
