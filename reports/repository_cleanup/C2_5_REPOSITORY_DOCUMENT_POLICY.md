# C2.5 — Repository Document Policy

> Policy for what documentation belongs in Git vs what stays ignored as
> generated artifacts.

---

## Policy

### Rule 1: Project documentation IS tracked

Documentation that describes repository state, decisions, audits, and cleanup
history belongs in Git. These are long-lived artifacts that future developers
and agents need.

**Tracked paths:**

| Path | Content | Created By |
|------|---------|------------|
| `reports/repository_audit/` | C1 audit reports, C2 merge blocker resolution | Sprint C1, C2 |
| `reports/repository_cleanup/` | C3 cleanup reports, keyword reviews, validation | Sprint C3.1, C3.2, C2.5 |
| `docs/Architecture.md` | Platform architecture | Architecture work |
| `docs/principles/` | Engineering principles | Architecture work |
| `docs/decisions/ADR-*.md` | Architectural Decision Records | Decision process |
| `docs/reviews/` | Code review records | Review process |
| `docs/research/` | Research notes | Research process |
| `docs/knowledge/` | Knowledge gap documents | Investigation |
| `knowledge/` | Project knowledge base | All sprints |
| `AGENTS.md` | Master agent policy | Agent system |
| `SKILLS.md` | Skill inventory | Agent system |
| `PROJECT_MATURITY.md` | Maturity assessment | Assessment |

### Rule 2: Generated runtime artifacts are NOT tracked

Anything produced by a test run, benchmark execution, or investigation script
is a generated artifact. These are reproducible and should not pollute Git.

**Ignored paths:**

| Pattern | Content | Example |
|---------|---------|---------|
| `/reports/*` (except exceptions) | All generated report output | `reports/benchmark/`, `reports/stability/` |
| `output.xml` | Robot Framework output | Root-level |
| `log.html` | Robot Framework log | Root-level |
| `report.html` | Robot Framework report | Root-level |
| `*.log` | Log files | API capture logs, debug logs |
| `*.local.yaml` | Local test data (PII) | `ntb.local.yaml` |
| `*.secret.yaml` | Secret test data | Credentials |
| `.env` | Environment variables | Secrets |
| `*.apk` | APK binaries | `apps/android/app.apk` |
| `*.pyc` | Python bytecode | `__pycache__/` |
| `__pycache__/` | Python cache directories | Various |
| `.DS_Store` | macOS metadata | Various |
| `node_modules/` | Node dependencies | Root |
| `.opencode/` | Opencode local config | Root |

### Rule 3: New documentation directories

When creating a new documentation directory under `reports/`, add a `!` exception
in `.gitignore`:

```gitignore
/reports/*
!/reports/repository_audit/
!/reports/repository_cleanup/
!/reports/<new_documentation_dir>/   # Add here
```

**Criteria for tracking a `reports/` subdirectory:**
1. Contains only hand-authored documentation (`.md`, `.txt`)
2. Does NOT contain generated artifacts (`.png`, `.xml`, `.json`, `.log`)
3. Describes repository state, decisions, or process — not runtime output
4. Is not reproducible by running a test

### Rule 4: Generated artifacts within tracked directories

If a tracked documentation directory accidentally contains a generated artifact
(e.g., a screenshot placed in `reports/repository_audit/`), it should be removed
or the following additional ignore rules should be added:

```gitignore
/reports/repository_audit/*
!/reports/repository_audit/*.md
```

This would track only `.md` files and ignore everything else.

**Current state:** Both documentation directories contain only `.md` files.
No additional rules needed at this time.

---

## Document Lifecycle

```
Sprint produces documentation
    ↓
Documentation goes to reports/repository_audit/ or reports/repository_cleanup/
    ↓
.gitignore exception allows tracking
    ↓
git add reports/repository_audit/<file>.md
    ↓
Committed with sprint changes
    ↓
Future sprints can read documentation from Git history
```

### What does NOT go in Git

```
Test run produces output
    ↓
Robot writes to reports/<run_name>/
    ↓
.gitignore /reports/* ignores it
    ↓
Stays in working tree only
    ↓
Developer cleans up or keeps locally
    ↓
Never committed
```

---

## Current .gitignore (after C2.5)

```gitignore
# IDE
.idea/
.vscode/

# Robot Framework
/reports/*
!/reports/repository_audit/
!/reports/repository_cleanup/
output.xml
log.html
report.html

# Python
__pycache__/
*.pyc

# Mac
.DS_Store

# APK
apps/android/*.apk

# Local sensitive test data
*.local.yaml
*.secret.yaml
.env

# Logs
*.log

# Dependencies
node_modules/
.opencode/
```

---

## Compliance Check

| Criterion | Status |
|-----------|--------|
| Repository reports (audit, cleanup) are trackable | PASS |
| Generated runtime artifacts remain ignored | PASS |
| Root Robot outputs remain ignored | PASS |
| PII test data remains ignored | PASS |
| APK binaries remain ignored | PASS |
| Python cache remains ignored | PASS |
| No runtime behavior change | PASS |
| No Robot Framework logic modified | PASS |
| No Page Objects modified | PASS |
| No locators modified | PASS |
| Minimal diff (1 line changed, 2 added) | PASS |
