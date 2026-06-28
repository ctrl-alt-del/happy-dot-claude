---
name: gitignore-hardening
description: Audit and harden a Git repository's .gitignore to prevent leaking secrets and sensitive info (keystores, .env files, API keys, certificates, cloud credentials, IDE/editor config), and stop tracking files that were already committed. Use this whenever the user mentions hardening or updating .gitignore, preventing secret or credential leaks, accidentally committing keys or .env files, securing a repo before pushing or making it public, untracking already-committed files, or cleaning IDE config out of a repo — even if they only say something like "make sure I'm not leaking anything" or "fix my gitignore".
---

# Gitignore Hardening

Harden a repository against leaking sensitive information through Git. The job has two distinct halves that people routinely conflate:

1. **Prevent future leaks** — make `.gitignore` cover the secret-bearing files this project produces.
2. **Stop leaking what's already tracked** — `.gitignore` does nothing to files Git already tracks; those need `git rm --cached` (and, if real secrets were exposed, history scrubbing + rotation).

Keeping these two halves separate in your head is the whole game. A common and dangerous mistake is to add a pattern to `.gitignore` and assume the file is now safe, when in fact it remains tracked and keeps getting committed.

## Workflow

### 1. Understand the project before touching anything

Figure out the ecosystem(s) so you know which sensitive files are even relevant — an Android project leaks keystores, a Node project leaks `.env`, a Python project leaks `*.pem` and virtualenvs, a Terraform project leaks `*.tfstate`. Guessing generic patterns is fine as a floor, but tailoring to the actual stack is what makes this useful.

```bash
git rev-parse --is-inside-work-tree   # confirm it's a repo
ls -a                                  # spot manifest files: package.json, build.gradle.kts, pyproject.toml, go.mod, etc.
```

Read `references/patterns.md` for the curated, per-ecosystem pattern lists. Pull in the sections that match what you found, plus the "universal secrets" section that applies everywhere.

### 2. Audit what is currently tracked or present

This is the step people skip, and it's the one that catches active leaks. Check both what's on disk and — more importantly — what Git is already tracking.

```bash
# Sensitive-looking files currently tracked by Git (the real risk):
git ls-files | grep -iE '\.(env|pem|key|p12|pfx|jks|keystore|cer|der)$|(^|/)\.env|secret|credential|\.idea/|\.vscode/'

# Sensitive-looking files present on disk (tracked or not):
find . -type f \( -iname '*.jks' -o -iname '*.keystore' -o -iname '*.p12' \
  -o -iname '*.pem' -o -iname '*.key' -o -iname '.env*' -o -iname '*secret*' \
  -o -iname 'google-services.json' \) \
  -not -path './.git/*' -not -path '*/build/*' -not -path '*/node_modules/*'
```

For anything that looks sensitive, confirm whether Git already ignores it so you don't chase a non-problem:

```bash
git check-ignore -v <path>   # prints the matching rule, or nothing if not ignored
```

Distinguish three buckets, because each needs different handling:

- **Already ignored** — nothing to do.
- **Present but untracked, not yet ignored** — add a pattern (step 3); no untracking needed.
- **Already tracked** — add a pattern AND untrack it (step 4), AND assess whether the contents are real live secrets that need rotation (step 5).

### 3. Add patterns to `.gitignore`

Append the relevant patterns. Prefer collapsing redundant granular rules into a single broad one when it's clearly correct — e.g. replacing a handful of `/.idea/<specific-file>` lines with `/.idea` once you've confirmed the whole directory should be ignored. Group additions under comment headers so the file stays legible and the next person understands the intent.

Be deliberate about broad globs. `*.key` is usually safe, but verify it won't swallow a legitimate tracked source file (check `git ls-files | grep '\.key$'` first). When a pattern would match something that must stay tracked, scope it (`/secrets/*.key`) or add a negation (`!keep-this.key`) rather than dropping the protection.

For monorepos, decide whether the rule belongs in the root `.gitignore` or a module-level one; secret patterns are almost always best at the root so they apply everywhere.

### 4. Untrack files that are already committed

`.gitignore` is ignored for files Git already tracks. Remove them from the index while keeping them on disk:

```bash
git rm --cached <path>           # single file
git rm -r --cached <dir>         # directory, e.g. .idea
```

`--cached` is the safety belt: it deletes Git's tracking, not the user's local file. After this, the file shows as deleted in the index and — assuming a matching `.gitignore` rule — becomes ignored going forward. Verify:

```bash
git check-ignore -v <path>       # should now print the rule
```

### 5. If real secrets were already committed, say so plainly

Untracking removes a secret from the *current* tree, but it remains in every prior commit and in any clone, fork, or remote. If the audit turned up genuine live credentials (a private key, an API token, a populated `.env`) that were ever committed, the `.gitignore` fix is necessary but **not sufficient**. Tell the user directly that:

- The secret is still recoverable from history and must be treated as **compromised** — the durable fix is to **rotate/revoke** it at the source (regenerate the key, roll the token).
- History rewriting (`git filter-repo`, or the BFG Repo-Cleaner) can purge the blob, but it rewrites commit hashes and requires coordination with anyone who has cloned/forked. Offer it as a follow-up; don't silently run it.

Rotation matters more than scrubbing. A leaked-then-deleted secret that's still valid is still a breach; a rotated secret in old history is harmless.

### 6. Commit, with separated concerns

Stage the `.gitignore` edits alongside the `git rm --cached` deletions and commit them together with a message that names both actions, so the history is self-explanatory:

```bash
git add .gitignore
git commit -m "Harden .gitignore and stop tracking <whatever was untracked>"
```

Then re-verify nothing sensitive is still tracked: rerun the `git ls-files | grep ...` audit from step 2 and confirm it comes back clean (or only with things the user intentionally keeps).

## Worked example

A fresh Android (Gradle/Compose) project had committed its `.idea/*.xml` IDE files in the initial commit, and the `.gitignore` had no coverage for signing keys or secrets.

- **Audit:** `git ls-files` showed `.idea/AndroidProjectSystem.xml`, `gradle.xml`, `misc.xml`, `runConfigurations.xml`, `vcs.xml` tracked. `local.properties` was already ignored (verified with `git check-ignore`). No live keystores or `.env` present — so this was preventative for secrets, but a real fix for the tracked IDE config.
- **`.gitignore`:** collapsed the granular `/.idea/caches`, `/.idea/workspace.xml`, … lines into a single `/.idea`, and appended grouped sections for keystores (`*.jks`, `*.keystore`, `keystore.properties`), API-key property files, certificates (`*.p12`, `*.pem`, `*.key`), and `google-services.json`.
- **Untrack:** `git rm -r --cached .idea` removed the six tracked files from the index while leaving them on disk.
- **Verify + commit:** `git check-ignore -v .idea/misc.xml` confirmed the new `/.idea` rule matched; committed both changes together as "Harden .gitignore and stop tracking .idea IDE files".

Note there were no live secrets here, so no rotation was needed — but the IDE files were flagged as low-sensitivity local/personal config rather than credentials, and the user was told as much.

## Reference files

- `references/patterns.md` — Curated `.gitignore` patterns organized by ecosystem (universal secrets, Android/JVM, Node, Python, cloud/IaC, editors/OS). Read it in step 1 and pull in the sections that match the detected stack.
