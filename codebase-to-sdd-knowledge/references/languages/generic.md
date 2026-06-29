# Generic Analysis (Any Language)

Use this when the detected language doesn't have a specific strategy file,
or as a supplement for mixed-language projects.

## Adapting the workflow

Without language-specific tooling, rely on:
- File extensions to classify source files
- `rg` (ripgrep) for pattern-based search
- Directory structure for module boundaries
- Config files for dependencies
- Git history for hotspots and ownership

## Language-agnostic detection

### Find the dominant language
```bash
# Count files by extension, sorted by frequency
find . -type f -not -path './node_modules/*' -not -path './.git/*' -not -path '*/target/*' -not -path '*/vendor/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10
```

### Find source directories
```bash
# Directories with the most source files (exclude .git, node_modules, vendor, target)
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.swift" -o -name "*.kt" -o -name "*.scala" -o -name "*.ex" -o -name "*.exs" -o -name "*.php" -o -name "*.dart" \) -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/target/*' | xargs dirname | sort | uniq -c | sort -rn | head -15
```

### Identify the build system
Look for these files at the project root:
- `Makefile` — Make
- `CMakeLists.txt` — CMake (C/C++)
- `build.gradle` or `build.gradle.kts` — Gradle (Java/Kotlin)
- `pom.xml` — Maven (Java)
- `mix.exs` — Mix (Elixir)
- `Gemfile` — Bundler (Ruby)
- `composer.json` — Composer (PHP)
- `Package.swift` — Swift Package Manager
- `pubspec.yaml` — Dart/Flutter
- `build.sbt` — sbt (Scala)

### Identify the test framework
Look for these patterns:
- `test/` or `tests/` or `spec/` or `__tests__/` directory
- Files matching `*_test.*`, `*.test.*`, `*_spec.*`, `*.spec.*`, `test_*.*`
- Dependencies containing `test`, `junit`, `pytest`, `rspec`, `minitest`

## Pattern-based analysis (works for any language)

### Data models
```bash
# Search for data definition keywords across common languages
rg -i "schema\b|entity\b|model\b|struct\b|type\b|interface\b|class\b" --include="*.{go,rs,py,ts,js,java,kt,rb,swift,php,dart,scala,ex,exs}" | head -40
```

### API endpoints
```bash
# Search for HTTP method patterns
rg -i "\.get\(|\.post\(|\.put\(|\.delete\(|\.patch\(|route\(|handle\b|endpoint\b|controller\b" --include="*.{go,rs,py,ts,js,java,kt,rb,php,ex,exs}" | head -40
```

### Configuration
```bash
# Search for environment variable usage
rg "env\.|ENV\[|process\.env\.|getenv\(|os\.environ|dotenv|config|settings" --include="*.{go,rs,py,ts,js,java,kt,rb,php}" | head -30
```

### Error handling
```bash
# Search for error patterns
rg "error\b|exception\b|panic\b|throw\b|raise\b|catch\b|rescue\b|recover\b" --include="*.{go,rs,py,ts,js,java,kt,rb,php,swift}" | head -30
```

### TODO/FIXME/HACK
```bash
rg "TODO|FIXME|HACK|WORKAROUND|XXX|OPTIMIZE|BUG" --include="*.{go,rs,py,ts,js,java,kt,rb,swift,php,c,cpp,h,dart,scala,ex,exs}" --no-heading
```

### Commented-out code
```bash
# Lines starting with comment markers that look like code
rg "^\s*(//|#|--|;;|%)\s*(if|for|while|function|def|fn|class|return|var|let|const|import|require)" --include="*.{go,rs,py,ts,js,java,kt,rb,php,swift}" --no-heading | head -20
```

## Universal gotchas to watch for

Regardless of language:
- **Secret leaks**: Check `.env.example` and config files for API keys,
  tokens, passwords. Check `.gitignore` for common secret patterns.
- **Missing error handling**: Functions that can fail but don't propagate
  errors — look for silent `catch` blocks, `/_` error discards (`_ =` in
  Go, `let _ =` in Rust, bare `except:` in Python)
- **Circular dependencies**: Files that import each other — harder to
  detect without language tools, but check for bidirectional imports in
  related files
- **Hardcoded values**: Magic numbers, hardcoded URLs, hardcoded ports —
  grep for IP addresses, localhost URLs, port numbers > 1024
- **Debug artifacts**: `console.log`, `println!`, `print(`, `fmt.Println`
  in production code — some are intentional (CLI output), some are leftover
  debug prints
- **Large files**: Files > 500 lines are harder to understand and test —
  flag them in `edges/tech-debt.md`
- **No tests**: Directories with source files but no corresponding test
  files — note in `gaps.md` or `edges/flaky-areas.md`

## When to do deeper analysis

If the project is in a language you know well but that doesn't have a
specific strategy file, adapt the closest existing strategy. The
TypeScript strategy is the most detailed and can serve as a template for
adding new language strategies.

If the project is in a language you don't know, focus on what you can
determine:
1. Structure (from directories and file names)
2. Dependencies (from config files)
3. Git history (hotspots, ownership, bugs)
4. Conventions (from reading patterns, not understanding semantics)

Flag what you're unsure about in `gaps.md`:
```markdown
## Unclear items (language: $LANGUAGE)
- [ ] The purpose of `src/foo/bar.xyz` — appears to handle data
  transformation but unable to verify
- [ ] Whether `src/routes/` uses middleware-based auth or manual checks
```
