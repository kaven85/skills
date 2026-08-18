---
name: commit-release
description: >
  Orchestrate the full code submission pipeline: inspect changes, check version/CHANGELOG,
  stage, run tests, write commit message, push, and release. Delegates message generation
  to caveman-commit and dangerous ops to git-guardrails. Works for any git repo.
  Use when user says: commit code, 提交代码, submit, bump version, 升级版本号,
  update changelog, push, release, 发布.
version: 1.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, commit, release, version, changelog, workflow, push, conventional-commits, pipeline]
    related_skills: [caveman-commit, git-guardrails-claude-code, code-review, resolving-merge-conflicts, setup-pre-commit]
---

# Commit & Release Workflow

## Relationship with Related Skills

This skill is the **workflow conductor** — it defines the sequence and decision points. Specialized steps delegate to these skills:

| Skill | Role | When to invoke |
|-------|------|---------------|
| `caveman-commit` | Generate ultra-compressed commit message | After staging, before commit |
| `code-review` | Review code quality against standards | Before commit, for large/infrastructure changes |
| `git-guardrails-claude-code` | Set up pre-action hooks | Once per project, for safety |
| `resolving-merge-conflicts` | Resolve git merge/rebase conflicts | When push fails due to conflict |
| `setup-pre-commit` | Set up Husky + lint-staged | Once per project, for formatting |

## Full Workflow

```mermaid
flowchart TD
    A([User: "commit code"]) --> B[git status]
    B --> C[git diff --stat]
    C --> D{有未提交改动?}
    D -->|否| Z([无事可做])
    D -->|是| E{Safe?}
    E -->|危险操作| E1[git-guardrails 拦截]
    E1 --> Z
    E -->|安全| F[Review diff 理解变更]
    F --> G{变更规模?}
    G -->|大 / 跨模块| G1[code-review → 修反馈]
    G1 --> H
    G -->|小 / 明确| H[检查版本号 + CHANGELOG]
    H --> I[Stage 代码 + 文档]
    I --> J[排除 artifacts]
    J --> K[跑测试门禁]
    K -->|失败| K1[修 bug 重跑]
    K1 --> K
    K -->|全绿| L{多个逻辑变更?}
    L -->|是| L1[拆分提交]
    L1 --> M
    L -->|否| M[写 commit message]
    M --> N[git commit]
    N --> O{推送前需确认?}
    O -->|共享分支 / 生产| O1[问用户确认]
    O1 --> P
    O -->|个人分支| P[git push]
    P -->|冲突| P1[resolving-merge-conflicts]
    P1 --> P
    P -->|成功| Q([完成])
    P -->|需创建 MR| R[提示创建 MR]
    R --> Q
```

## Stage 0: Pre-flight checks

### 0.1 Check branch and remote
```bash
git branch              # 确认当前分支
git remote -v           # 确认 remote 地址
git log --oneline -3    # 最近的提交风格，用于 message 参考
```

### 0.2 Safety: identify dangerous operations before starting
Items that need user confirmation before execution:
- `git push` to shared/protected branches (main, master, release/*)
- `git push --force` / `git push --force-with-lease` (any branch)
- `git reset --hard` / `git clean -fd`
- `git branch -D` (force delete branch)
- `git tag -d` / `git push --delete origin <tag>`
- `git revert` on a commit that's already been pushed

If `git-guardrails-claude-code` hooks are installed, dangerous ops are auto-blocked. Otherwise, ask before each.

### 0.3 Understand the diff
Read `git diff` (or `git diff --cached` if already staged) **before** writing the commit message. Never guess what changed. Identify:
- What changed (files, functions, logic)
- Why (surface from the conversation context)
- Type (feat / fix / refactor / docs / test / chore)
- Scope (which module/component)

## Stage 1: Version & Changelog

### 1.1 Read project conventions first
Different projects manage versions differently. Read project-level docs first (CLAUDE.md, CONTRIBUTING.md, SKILL.md, etc.):

**Common patterns:**
- `VERSION` file + frontmatter `version:` fields
- `package.json` / `Cargo.toml` / `pyproject.toml` / `pubspec.yaml`
- Multi-module versions (each sub-component independently versioned)
- No version file (plain repo, no release cycle)

### 1.2 Semver rules (when no project-specific versioning exists)
```
Given version MAJOR.MINOR.PATCH:
  MAJOR: breaking changes (incompatible API / behavior change)
  MINOR: new feature (backward-compatible)
  PATCH: bug fix / documentation / minor refactor (no new behavior)
```

### 1.3 Version consistency check
When bumping, verify **all** version declaration locations are consistent:
- If version is in multiple files, list them and check each
- If version constants exist in source code, check them
- If test assertions lock in version strings, update them

### 1.4 Changelog
- If `CHANGELOG.md` exists, append or update the entry for the new version
- Standard format: `## [X.Y.Z] - YYYY-MM-DD` with bullet list of changes
- If CHANGELOG was already updated (committed ahead of code), use that version — do NOT double-bump

### 1.5 Automated tooling fallback
If the project already has automated version/CHANGELOG tooling, delegate instead of hand-writing:
- **semantic-release**: auto-determines version bump from commit history, auto-generates CHANGELOG. If `.releaserc*` / `release.config.*` exist, run `npx semantic-release --dry-run` to preview.
- **release-please**: GitHub-native, driven by `release-please.yml`. Let the existing CI handle it.
- **changesets**: version + CHANGELOG from `.changeset/` markdown files. Run `npx changeset version` to apply.
- **commitlint**: enforces Conventional Commits format via `husky` or CI. If configured, verify the project's rules (check `commitlint.config.*`). Consider `setup-pre-commit` for new projects.

## Stage 2: Staging

### 2.1 Stage the right files
```bash
# Explicit paths — never `git add .` or `git add -A` without review
git add <file1> <file2> <dir/>

# Verify
git status --short
```

### 2.2 What to NEVER stage
Read `.gitignore` first. Then apply these generic rules:

| Category | Examples | Rule |
|----------|----------|------|
| Build artifacts | `dist/`, `build/`, `*.zip`, `*.exe`, `*.wasm` | Never stage |
| Dependencies | `node_modules/`, `vendor/`, `.venv/` | Never stage (in .gitignore) |
| Config with local paths | `.env`, `.env.local`, `settings.json` | Never stage (unless explicitly told) |
| Editor/IDE files | `.vscode/`, `.idea/`, `*.swp` | Never stage (in .gitignore) |
| OS files | `.DS_Store`, `Thumbs.db` | Never stage (in .gitignore) |
| Lock files | `package-lock.json` is tracked; `*.lock` otherwise | Check project convention |
| Generated metadata | `__pycache__/`, `.pytest_cache/`, `.eslintcache` | Never stage |
| Credentials | `*_session.json`, `*.pem`, `*key*`, `*.cred` | Never stage |
| Large binaries | `*.mp4`, `*.psd`, `*.ai`, `*.bak` | Never stage |
| Tool logs | `.playwright-mcp/`, `*.log`, `debug/` | Never stage |
| Unrelated untracked | Files outside the scope of this commit | Never stage |

### 2.3 One logical change per commit
If the working tree contains **multiple independent changes**, split them:

```bash
# Stage only the files for the first commit
git add <first-change-files>
git commit -m "..."

# Then the second batch
git add <second-change-files>
git commit -m "..."

### 2.4 Optional: pre-commit hooks
If the project lacks automated commit gates, consider `setup-pre-commit` (Husky + lint-staged) for formatting and `commitlint` (`@commitlint/cli` + `@commitlint/config-conventional`) for Conventional Commits enforcement at commit time. These are one-time setups — ask the user before installing.

Tests: **One change should have one message that explains it.** A commit titled "fix search and add login page" is two commits.

## Stage 3: Test Gate

Classify the change before choosing verification. Do not run TDD or a full test suite by default.

Before running any verification command, output this decision record:

```text
改动类型: <functional | non-functional | unclear>
判断依据: <从 diff 中观察到的具体行为或文件改动>
选用的验证门禁: <TDD verification | 最小相关回归/构建/类型检查/lint | 轻量文档或配置检查>
```

Use `functional` only when the diff changes user-observable behavior. Use `non-functional` for behavior-preserving, documentation, metadata, build, CI, or configuration changes. If the evidence is insufficient, use `unclear`, explain what is missing, and ask the user to classify it before running verification.

| Change type | Required verification |
|---|---|
| Functional `feat` / `fix` that changes user-observable behavior | **TDD verification required.** Explicitly state that TDD applies, confirm a focused behavior test was added or updated, exercise the affected public behavior, and run the smallest relevant test command. During implementation, use the red → green loop: write the failing test first, then make it pass. |
| `refactor`, `perf`, `build`, `ci`, or dependency changes with no intended behavior change | No TDD requirement. Run only the smallest relevant regression, build, type-check, lint, or configuration validation. |
| `docs`, `style`, `chore`, metadata, or changelog-only changes | No TDD requirement. Run a lightweight applicable check (for example Markdown lint, schema validation, or a diff review); if none exists, record that no automated check applies. |

Never commit code that breaks an applicable check. If the change classification is unclear, ask the user before selecting a test gate.

When describing a verification plan, label the functional path as “TDD verification” and distinguish it from lightweight non-functional checks. This makes the selected gate auditable before any command runs.

```bash
# Python
python -m pytest tests/ -x -q
python3 -m pytest tests/ -x -q

# Node / TypeScript
npm test
pnpm test
bun test

# Rust
cargo test

# Go
go test ./...

# No test framework — at least smoke-test the changed module
python3 -c "from scripts.mymodule import something; something()"
```

**Rules:**
- If tests fail, diagnose and fix before committing. Do not commit with "tests will be fixed later"
- For functional changes, confirm the focused test covers the intended behavior or bug reproduction
- For non-functional changes, do not add a TDD gate solely because files changed
- Only run the relevant, smallest verification; do not run the entire project CI by default

## Stage 4: Commit Message

### 4.1 Generate the message

**Delegate to `caveman-commit` for the base format.** It covers: type/scope/subject format, subject line rules (imperative mood, ≤72 chars, no trailing period), body rules (only for why, wrap at 72, `Closes #42`), breaking change format (`!` + `BREAKING CHANGE:`), and the NEVER list. Load it before generating the message.

### 4.1.1 Conventional Commits 1.0.0 baseline

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) as the canonical message format unless the project documents a stricter convention (for example, `commitlint`).

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Rules required by the specification:
- `type` is required and must be a noun. Use `feat` for a new feature and `fix` for a bug fix; project-specific additional types are allowed.
- `scope` is optional and, when present, is a parenthesized noun that identifies a codebase area: `feat(auth): add passkey login`.
- The `:` and following single space are required; the short description starts immediately after them.
- A body is optional, free-form, and starts one blank line after the description.
- Footers are optional and start one blank line after the body (or description). Use either `Token: value` or `Token #value`; footer tokens use hyphens instead of spaces, except `BREAKING CHANGE`.
- A breaking change must use `!` immediately before `:` and/or an uppercase `BREAKING CHANGE: <description>` footer. `BREAKING-CHANGE:` is equivalent as a footer token.

SemVer guidance from the specification: `fix` normally maps to PATCH, `feat` to MINOR, and any breaking change to MAJOR. Do not infer a release bump when project-specific release tooling defines a different policy.

### 4.2 Additional rules (not covered by caveman-commit)

**Type reference (Conventional Commits 1.0.0):**
| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Restructure, no behavior change |
| `perf` | Performance improvement |
| `docs` | Documentation only |
| `test` | Tests only |
| `chore` | Maintenance, build, release |
| `build` | Build system / dependencies |
| `ci` | CI configuration |
| `style` | Formatting, no logic change |
| `revert` | Revert a prior commit |

**Multi-change merge commit:** when a single commit bundles multiple related changes, body lists each change as bullet:
```
feat(scope): main change + secondary changes

- file.py: what changed
- another.py: what changed
- 版本: component X.Y.Z, sub-component A.B.C
```

**Emoji convention:** if the project's commit history uses emoji (gitmoji/git-cz), continue the convention. Otherwise, do not introduce emoji unless the user asks. The `commit-workflow` skill by drvoss provides a full type→emoji mapping if needed.

### 4.3 What NEVER goes in commit messages
- Restating the file name when scope already says it
- AI attribution (unless project rule requires `Assisted-by`/`Co-authored-by` trailer)
- Emoji (unless the project convention requires)
## Stage 5: Commit

```bash
git commit -m "type(scope): subject"
# or for multi-line
git commit -m "type(scope): subject" -m "body line 1
body line 2"
```

**Post-commit checks:**
- `git log --oneline -1` — verify the message looks right
- `git status` — confirm no leftover staged/unstaged files

## Stage 6: Push

### 6.1 Pre-push confirmation
**Always ask before:**
- Pushing to shared/protected branches (main, master, release/*, production)
- Pushing with `--force` / `--force-with-lease` (any branch)
- Creating or pushing tags (`git tag`, `git push --tags`, `git push origin <tag>`) — ask before creating AND before pushing
- Pushing to a branch others are actively working on

Personal feature branches can be pushed without confirmation (unless guarded by `git-guardrails`).

For every listed operation, state the exact operation and ask a direct question such as: “`main` is a shared branch. Do you want me to run `git push origin main`?” Do not run the command until the user gives an affirmative answer. This confirmation gate also applies when explaining a plan: explicitly identify the confirmation required before the later command.

### 6.2 Push
```bash
git push origin <branch>
```

### 6.3 Conflicts
If push fails with non-fast-forward:
```bash
git pull --rebase origin <branch>
# resolve conflicts (delegate to resolving-merge-conflicts if needed)
git push origin <branch>
```

### 6.4 MR/PR creation
After push, if the user is working on a feature branch, offer to create a merge request / pull request (if the platform CLI is available, e.g. `gh`, `glab`).

## Stage 7: Release

A release is a specific type of commit with:
- Version bump (MAJOR or MINOR, not PATCH; PATCH can be a regular commit)
- CHANGELOG entry for the new version
- Tag (if project convention requires)
- Message: `chore: release vX.Y.Z`

```bash
# Standard release
git add VERSION CHANGELOG.md
git commit -m "chore: release vX.Y.Z"
# Ask the user before creating a tag.
git tag vX.Y.Z               # optional — check project convention
# Ask the user again before pushing main or the tag.
git push origin main
git push origin vX.Y.Z        # if tag was created
```

## Stage 8: Error Recovery

### 8.1 Fix last commit message
```bash
# Only if not pushed yet
git commit --amend -m "new message"
```

### 8.2 Unstage a file
```bash
git reset HEAD <file>
```

### 8.3 Undo last commit (keep changes)
```bash
# Only if not pushed yet
git reset --soft HEAD~1
```

### 8.4 Revert a pushed commit
```bash
git revert <commit-hash>
# Creates a new commit that undoes the changes
```


### 8.5 Known Issues pattern
If you encounter reproducible failure patterns (publish race conditions, hook conflicts, lockfile drift), document them in this skill's `references/known-issues.md` with the trigger, symptom, and verified fix. The `release` skill by terrylica maintains an extensive known-issues catalog for reference.

## Verification Checklist

- [ ] 变更类型判断正确（feat / fix / refactor / docs / test / chore / build / ci / revert）
- [ ] 分支确认：当前分支正确，不往 protected branch 直接推（除非明确允许）
- [ ] 版本号所有位置一致（若有版本号）
- [ ] CHANGELOG 已含当前变更（或已写入）
- [ ] 未 stage 任何 artifact / 本地配置 / 无关文件
- [ ] 拆分提交：一个逻辑变更一个 commit
- [ ] 测试全绿
- [ ] Commit message subject ≤72 chars, imperative mood, no trailing period
- [ ] Body 只写 why（diff 不包含的信息），不重述 diff
- [ ] 推送前确认分支安全
- [ ] Push 成功，remote 无冲突
- [ ] 若 feature branch，提示创建 MR/PR
