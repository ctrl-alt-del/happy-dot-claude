# Gitignore Patterns by Ecosystem

Curated patterns for hardening `.gitignore`. Always apply **Universal secrets**; then add the section(s) matching the detected stack. These are a starting point — adapt to what the audit actually found rather than pasting everything blindly.

## Contents

- [Universal secrets (apply everywhere)](#universal-secrets-apply-everywhere)
- [Android / JVM / Gradle](#android--jvm--gradle)
- [Node / JavaScript / TypeScript](#node--javascript--typescript)
- [Python](#python)
- [Cloud & Infrastructure-as-Code](#cloud--infrastructure-as-code)
- [Editors & OS cruft](#editors--os-cruft)

---

## Universal secrets (apply everywhere)

These hold credentials regardless of language and should be ignored in essentially every repo.

```gitignore
# Environment / dotenv
.env
.env.*
!.env.example
!.env.template

# Private keys & certificates
*.pem
*.key
*.p12
*.pfx
*.cer
*.der
id_rsa
id_ed25519
*.ppk

# Generic secret/credential files
secrets.*
*.secret
credentials.json
credentials.yml
*-credentials.json
service-account*.json
```

Note the negations for `.env.example` / `.env.template`: teams intentionally commit those as documented placeholders, so keep them tracked.

## Android / JVM / Gradle

```gitignore
# Signing / keystores
*.jks
*.keystore
keystore.properties
signing.properties
release-signing.properties

# Local SDK paths (often holds machine-specific info)
local.properties

# Firebase / Google services (embed API keys)
google-services.json

# Build & IDE
/build
**/build/
.gradle
/.idea
*.iml
/captures
```

`local.properties` is the classic Android leak — it points at the local SDK and sometimes holds injected keys. Keep it ignored.

## Node / JavaScript / TypeScript

```gitignore
# Dependencies & build
node_modules/
dist/
build/
.next/
.nuxt/
out/
coverage/

# Env & secrets
.env
.env.local
.env.*.local

# npm/yarn auth — these can contain registry tokens
.npmrc
.yarnrc.yml
```

`.npmrc` deserves attention: a project-level `.npmrc` frequently contains a `//registry.../:_authToken=` line, which is a live credential. Ignore it unless you've confirmed it carries only non-secret config.

## Python

```gitignore
# Byte-compiled / caches
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtual environments
.venv/
venv/
env/

# Packaging & distribution
*.egg-info/
dist/
build/

# Env & secrets
.env
*.pem
instance/        # Flask instance folder often holds config secrets
```

## Cloud & Infrastructure-as-Code

State and var files here routinely contain secrets in plaintext — treat them as high-risk.

```gitignore
# Terraform
*.tfstate
*.tfstate.*
*.tfvars
!example.tfvars
.terraform/
crash.log

# Kubernetes / Helm
kubeconfig
*.kubeconfig

# Cloud CLIs
.aws/credentials
.azure/
gcloud-service-key.json
```

`*.tfstate` is especially dangerous: Terraform writes resource attributes (including passwords and keys) into state in cleartext. If one was ever committed, treat its contents as compromised and rotate.

## Editors & OS cruft

Low-sensitivity (rarely secrets) but leaks local/personal config and creates noise. Worth ignoring; flag to the user that these are "info/privacy" rather than "credential" concerns.

```gitignore
# JetBrains
/.idea
*.iml

# VS Code (keep shared config if the team wants it)
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json

# macOS / Windows / Linux
.DS_Store
Thumbs.db
desktop.ini
*~
```
