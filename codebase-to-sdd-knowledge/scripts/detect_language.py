#!/usr/bin/env python3
"""Detect the primary language, build system, and tooling of a project.

Usage:
    python detect_language.py /path/to/project

Output: JSON to stdout with keys:
    language, build_system, test_cmd, lint_cmd, is_monorepo, package_manager
"""

import json
import os
import sys


LANGUAGE_MARKERS = {
    "typescript": {
        "extensions": {".ts", ".tsx"},
        "configs": ["tsconfig.json", "tsconfig.base.json"],
        "build_systems": {
            "npm": ["package.json", "package-lock.json"],
            "yarn": ["yarn.lock"],
            "pnpm": ["pnpm-lock.yaml", "pnpm-workspace.yaml"],
            "bun": ["bun.lockb", "bun.lock"],
        },
        "test_commands": {
            "jest": "npx jest",
            "vitest": "npx vitest run",
            "mocha": "npx mocha",
        },
        "lint_commands": {
            "eslint": "npx eslint .",
            "oxlint": "npx oxlint .",
            "biome": "npx biome lint .",
            "prettier": "npx prettier --check .",
        },
    },
    "python": {
        "extensions": {".py", ".pyi"},
        "configs": ["pyproject.toml", "setup.py", "setup.cfg"],
        "build_systems": {
            "pip": ["requirements.txt"],
            "poetry": ["poetry.lock"],
            "pipenv": ["Pipfile"],
            "uv": ["uv.lock"],
        },
        "test_commands": {
            "pytest": "pytest",
            "unittest": "python -m unittest",
        },
        "lint_commands": {
            "ruff": "ruff check .",
            "flake8": "flake8 .",
            "pylint": "pylint src/",
            "mypy": "mypy src/",
        },
    },
    "go": {
        "extensions": {".go"},
        "configs": ["go.mod", "go.sum"],
        "build_systems": {
            "go": ["go.mod"],
        },
        "test_commands": {
            "go": "go test ./...",
        },
        "lint_commands": {
            "golangci-lint": "golangci-lint run",
            "go-vet": "go vet ./...",
        },
    },
    "rust": {
        "extensions": {".rs"},
        "configs": ["Cargo.toml", "Cargo.lock"],
        "build_systems": {
            "cargo": ["Cargo.toml"],
        },
        "test_commands": {
            "cargo": "cargo test",
        },
        "lint_commands": {
            "clippy": "cargo clippy -- -D warnings",
            "rustfmt": "cargo fmt -- --check",
        },
    },
    "java": {
        "extensions": {".java", ".kt"},
        "configs": ["build.gradle", "build.gradle.kts", "pom.xml", "settings.gradle"],
        "build_systems": {
            "gradle": ["build.gradle", "build.gradle.kts", "gradlew", "gradlew.bat"],
            "maven": ["pom.xml"],
        },
        "test_commands": {
            "gradle": "./gradlew test",
            "maven": "mvn test",
        },
        "lint_commands": {
            "gradle-checkstyle": "./gradlew check",
            "maven-checkstyle": "mvn checkstyle:check",
        },
    },
    "ruby": {
        "extensions": {".rb"},
        "configs": ["Gemfile", "Gemfile.lock", "Rakefile"],
        "build_systems": {
            "bundler": ["Gemfile"],
        },
        "test_commands": {
            "rspec": "bundle exec rspec",
            "minitest": "bundle exec rake test",
        },
        "lint_commands": {
            "rubocop": "bundle exec rubocop",
        },
    },
    "elixir": {
        "extensions": {".ex", ".exs"},
        "configs": ["mix.exs", "mix.lock"],
        "build_systems": {
            "mix": ["mix.exs"],
        },
        "test_commands": {
            "mix": "mix test",
        },
        "lint_commands": {
            "credo": "mix credo",
        },
    },
    "php": {
        "extensions": {".php"},
        "configs": ["composer.json", "composer.lock"],
        "build_systems": {
            "composer": ["composer.json"],
        },
        "test_commands": {
            "phpunit": "./vendor/bin/phpunit",
            "pest": "./vendor/bin/pest",
        },
        "lint_commands": {
            "phpcs": "./vendor/bin/phpcs",
            "phpstan": "./vendor/bin/phpstan analyse",
        },
    },
    "swift": {
        "extensions": {".swift"},
        "configs": ["Package.swift", "*.xcodeproj", "*.xcworkspace"],
        "build_systems": {
            "spm": ["Package.swift"],
            "xcode": ["*.xcodeproj"],
        },
        "test_commands": {
            "spm": "swift test",
            "xcode": "xcodebuild test",
        },
        "lint_commands": {
            "swiftlint": "swiftlint",
        },
    },
    "dart": {
        "extensions": {".dart"},
        "configs": ["pubspec.yaml", "pubspec.lock"],
        "build_systems": {
            "dart": ["pubspec.yaml"],
        },
        "test_commands": {
            "dart": "dart test",
            "flutter": "flutter test",
        },
        "lint_commands": {
            "dart": "dart analyze",
            "flutter": "flutter analyze",
        },
    },
}


def count_extensions(root, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {".git", "node_modules", "vendor", "target", "__pycache__",
                        ".venv", "venv", ".tox", "dist", "build", ".next",
                        ".turbo", "coverage", ".nyc_output"}

    counts = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs
                       and not d.startswith(".") or d in {".github"}]
        for f in filenames:
            _, ext = os.path.splitext(f)
            if ext:
                counts[ext.lower()] = counts.get(ext.lower(), 0) + 1
    return counts


def detect_language(root):
    ext_counts = count_extensions(root)

    best_lang = "generic"
    best_score = 0

    for lang, info in LANGUAGE_MARKERS.items():
        score = 0
        for ext in info["extensions"]:
            score += ext_counts.get(ext, 0)
        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang


def detect_build_system(root, lang_info):
    for system, files in lang_info.get("build_systems", {}).items():
        for f in files:
            if os.path.exists(os.path.join(root, f)):
                return system
    return "unknown"


def detect_test_command(root, lang_info):
    for tool, cmd in lang_info.get("test_commands", {}).items():
        if tool == "gradle" and (os.path.exists(os.path.join(root, "gradlew"))
                                 or os.path.exists(os.path.join(root, "build.gradle"))
                                 or os.path.exists(os.path.join(root, "build.gradle.kts"))):
            return cmd
        if tool == "maven" and os.path.exists(os.path.join(root, "pom.xml")):
            return cmd
        if tool == "go" and os.path.exists(os.path.join(root, "go.mod")):
            return cmd
        if tool == "cargo" and os.path.exists(os.path.join(root, "Cargo.toml")):
            return cmd
    return lang_info.get("test_commands", {}).get(
        next(iter(lang_info.get("test_commands", {})), ""), ""
    )


def detect_lint_command(root, lang_info):
    for tool, cmd in lang_info.get("lint_commands", {}).items():
        if tool == "eslint" and os.path.exists(os.path.join(root, ".eslintrc.js")):
            return cmd
        if tool == "eslint" and os.path.exists(os.path.join(root, ".eslintrc.json")):
            return cmd
        if tool == "eslint" and os.path.exists(os.path.join(root, "eslint.config.js")):
            return cmd
        if tool == "ruff" and os.path.exists(os.path.join(root, "pyproject.toml")):
            return cmd
    return lang_info.get("lint_commands", {}).get(
        next(iter(lang_info.get("lint_commands", {})), ""), ""
    )


def is_monorepo(root, lang):
    if lang == "typescript":
        if os.path.exists(os.path.join(root, "pnpm-workspace.yaml")):
            return True
        if os.path.exists(os.path.join(root, "lerna.json")):
            return True
        if os.path.exists(os.path.join(root, "nx.json")):
            return True
        if os.path.exists(os.path.join(root, "turbo.json")):
            return True
        pkg = os.path.join(root, "package.json")
        if os.path.exists(pkg):
            try:
                with open(pkg) as f:
                    data = json.load(f)
                if data.get("workspaces"):
                    return True
            except (json.JSONDecodeError, IOError):
                pass
    if lang == "rust":
        cargo = os.path.join(root, "Cargo.toml")
        if os.path.exists(cargo):
            try:
                with open(cargo) as f:
                    content = f.read()
                if "[workspace]" in content:
                    return True
            except IOError:
                pass
    if lang == "go":
        if os.path.exists(os.path.join(root, "go.work")):
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_language.py /path/to/project", file=sys.stderr)
        sys.exit(1)

    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    lang = detect_language(root)
    lang_info = LANGUAGE_MARKERS.get(lang, LANGUAGE_MARKERS["typescript"])
    build_system = detect_build_system(root, lang_info)
    test_cmd = detect_test_command(root, lang_info)
    lint_cmd = detect_lint_command(root, lang_info)
    mono = is_monorepo(root, lang)

    result = {
        "language": lang,
        "build_system": build_system,
        "test_cmd": test_cmd,
        "lint_cmd": lint_cmd,
        "is_monorepo": mono,
        "package_manager": build_system,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
