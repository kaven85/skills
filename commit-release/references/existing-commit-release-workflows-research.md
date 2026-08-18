# Existing Commit/Release Workflows Research

> 调研时间: 2026-08-05  
> 方法: Primary source only — official docs, source SKILL.md files, first-party specs  
> 对比对象: `~/.claude/skills/commit-release/SKILL.md` (v1.1.0)

## Executive Summary

**结论: 该 skill 值得保留，且在当前生态中没有完整等价物。** 市面上的 commit/release skills 分为两类——要么只写 commit message (`caveman-commit`, `commit-workflow` by drvoss)，要么是特定工具的发布管道 (`publish-cli` by cline, `release` by terrylica)。没有一个 skill 覆盖"理解 diff → 版本一致性 → CHANGELOG → 测试门禁 → 拆分提交 → commit message → push 安全确认 → 发布 → 出错恢复"的**完整编排工作流**。

**建议保留并优化**：删除已在 `caveman-commit` 重复的 message 格式细节，改为引用；补充 emoji/gitmoji 支持作为可选方案；补充 `commitlint` 集成建议；优化 agent 特定行为（自动推到个人分支、保护分支确认）。

---

## Sources Reviewed

### Primary Sources

| # | Source | Type | Relevance |
|---|--------|------|-----------|
| 1 | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) | Spec | Commit 格式规范，全行业标准 |
| 2 | [Claude Code Skills Official Docs](https://code.claude.com/docs/en/skills) | Official Docs | Skill 架构规范、frontmatter、invocation 机制 |
| 3 | [`commit-workflow` by drvoss](https://github.com/drvoss/everything-copilot-cli/blob/main/skills/workflow/commit-workflow/SKILL.md) | Source Code | Public commit-workflow skill，Conventional Commits + emoji |
| 4 | [`publish-cli` by cline](https://github.com/cline/cline/tree/HEAD/.cline/skills/publish-cli) | Source Code | 最完整的 CLI 发布 skill：10-step pipeline, SDK 依赖检查, release notes, tag, publish |
| 5 | [`release` by terrylica](https://github.com/terrylica/cc-skills/tree/HEAD/plugins/mise/skills/run-full-release) | Source Code | General release pipeline: preflight → version → publish → verify → postflight |
| 6 | [`commit` gist by Benjaminsson](https://gist.github.com/Benjaminsson/4687439e06d9136fea3cf7d625df994b) | Source Code | Standardize CI/commitlint/commit tooling for org repos |
| 7 | [`caveman-commit`](~/.claude/skills/caveman-commit/SKILL.md) | Source Code | Ultra-compressed commit message generator (local) |

### Secondary Sources (for context only)

- [claudeskills.info](https://claudeskills.info) — Skill directory, 确认了 `publish-cli`、`release`、`changelog-writer`、`github-code-review` 的存在
- [mcpmarket.com](https://mcpmarket.com) — 确认了大量 message-only commit skills 的存在（`semantic-git-commits`, `conventional-git-commits`, `write-commit-message` 等 8+ 个）

---

## Comparison Table

### Coverage Matrix

| 能力 | `commit-release` (ours) | `commit-workflow` (drvoss) | `publish-cli` (cline) | `release` (terrylica) | `caveman-commit` |
|------|:---:|:---:|:---:|:---:|:---:|
| **Diff 理解 (Stage 0)** | ✅ | ✅ (staged diff inspection) | ❌ | ❌ (preflight only) | ❌ |
| **版本一致性检查** | ✅ (多位置) | ❌ | ✅ (`package.json` only) | ❌ (交给 semantic-release) | ❌ |
| **CHANGELOG 更新** | ✅ | ❌ (refs `add-to-changelog`) | ✅ (manual drafting) | ❌ (semantic-release 自动) | ❌ |
| **Staging 安全规则** | ✅ (artifact 排除表) | ✅ (`git add -p` split) | ❌ | ❌ | ❌ |
| **拆分提交指导** | ✅ (单逻辑变更) | ✅ (核心卖点) | ❌ | ❌ | ❌ |
| **测试门禁** | ✅ (6 种语言) | ✅ (optional hooks) | ✅ (CI gates) | ❌ (preflight is tree-clean) | ❌ |
| **Commit Message 格式** | ✅ (11 types) | ✅ (13 types + emoji) | ❌ | ❌ | ✅ (ultra-compressed) |
| **Push 安全确认** | ✅ (protected branch gate) | ❌ | ✅ (ask before push) | ❌ | ❌ |
| **版本号 bump (semver)** | ✅ | ❌ | ✅ (patch/minor/major) | ✅ (semantic-release 自动) | ❌ |
| **发布流程 (tag + publish)** | ✅ (generic) | ❌ | ✅ (GitHub Actions + local) | ✅ (mise pipeline) | ❌ |
| **出错恢复** | ✅ (amend, unstage, soft reset, revert) | ❌ | ❌ | ✅ (known issues 文档) | ❌ |
| **Agent 特定行为** | ✅ (危险操作确认) | ❌ | ❌ | ❌ | ✅ (boundaries) |
| **Language runtime 无关** | ✅ | ✅ (但 PowerShell 示例) | ❌ (npm/monorepo 专用) | ❌ (mise 专用) | ✅ |
| **与相关 skill 协作** | ✅ (caveman-commit 等 5 个) | ✅ (refs `add-to-changelog`) | ❌ | ❌ | ❌ |
| **Emoji 支持** | ❌ | ✅ (gitmoji 映射表) | ❌ | ❌ | ❌ |
| **CI 集成建议** | ❌ | ❌ (pre-commit hooks) | ✅ (GitHub Actions) | ✅ (mise tasks) | ❌ |

### 关键缺口分析

| 缺口 | `commit-release` 当前 | 最佳实践源 | 优先级 |
|------|----------------------|-----------|--------|
| **Emoji/gitmoji** | 未覆盖 | `commit-workflow` 有完整 emoji→type 映射表 | Low |
| **commitlint 集成** | 未提及 | `Benjaminsson` gist 有完整 CI 集成 | Medium |
| **Message 格式细节冗余** | 有完整的 body/breaking change/footer 格式 | `caveman-commit` 已覆盖 | High (移除冗余) |
| **Jira/Issue ID 自动推导** | 未覆盖 | `Benjaminsson` gist 有分支名推导 | Low |
| **semantic-release 自动化** | 未提及 | `release` by terrylica, `publish-cli` | Medium (作为备选方案) |
| **Pre-commit hooks 建议** | 未提及 | `commit-workflow` 有 husky/lint 建议 | Medium |

---

## Necessity Assessment

### 为什么有必要

1. **工作流 conductor 的空缺**：市面上所有 commit skills 要么只生成 message（`caveman-commit`、mcpmarket 上 8+ 个 Conventional Commits generator），要么是特定工具（mise/semantic-release/GitHub Actions）的发布包装。**没有一个 skill 承担"从 untracked 改动到 push 完成的全程编排"角色。**

2. **版本一致性检查**：`publish-cli` 只检查 `package.json`，`release` 交给 semantic-release。但多组件项目（monorepo、多 version 文件、frontmatter）没有 skill 覆盖。我们的 skill 是唯一覆盖此场景的。

3. **Staging 安全规则**：`commit-workflow` 只关注 diff split，不关注 artifact 排除。我们的 skill 有完整的 10 类 artifact 排除表，对 AI agent 尤其重要（agent 可能盲目 `git add -A`）。

4. **Push 安全确认 + 出错恢复**：`publish-cli` 要求 push 前确认，但没有通用的保护分支策略和出错恢复。我们的 skill 有 protected branch gate + 4 种恢复操作。

5. **多 skill 协作**：明确引用 `caveman-commit`、`git-guardrails`、`code-review`、`resolving-merge-conflicts`、`setup-pre-commit`——避免重复，增加复用。

### 与其他 skill 的边界

- `caveman-commit` → 生成 commit message **文本**，不 stage、不 commit、不 push
- `commit-release` → 编排**全流程**：什么时候跑测试、什么时候调 caveman-commit、什么时候问用户确认 push
- `code-review` → 提交前的质量审查，commit-release 在 Stage 0 决策是否调用它
- `git-guardrails` → one-time setup on clean repos；commit-release relies on it being already installed

这个边界是清晰的，没有重叠。

---

## Optimization Recommendations

### 1. [High] 去重 — 减少 commit message 格式细节

`caveman-commit` 已经完整覆盖 Conventional Commits message 格式（subject ≤ 72, imperative mood, body ONLY for why, breaking change footer, NEVER 列表）。`commit-release` 的 Stage 4 有 ~60 行格式细节，与 `caveman-commit` 重叠 ~80%。

**改法**：Stage 4 改为引用 `caveman-commit` + 补充它不覆盖的部分（多变更合并提交、版本号尾注）。

### 2. [Medium] 补充 commitlint / pre-commit hooks

`Benjaminsson` gist 和 `commit-workflow` 都建议在 CI 中集成 `commitlint`。对于有新项目的用户，可以建议 setup。

**改法**：在 Stage 2 或 Verification Checklist 中加入"可选: 考虑 setup-pre-commit + commitlint"的提示，避免强依赖。

### 3. [Medium] 补充 semantic-release 作为备选

对于 Node.js 项目，`semantic-release` + `commitlint` 可以自动处理版本 bump + CHANGELOG + 发布。如果要处理非 Node 项目，可以手动实现这些步骤——这正是当前 skill 的重点。

**改法**：在 Stage 1 (Version & Changelog) 加入"如果项目已有 semantic-release / release-please / changesets，委托给它们"的 fallback。

### 4. [Low] 补充 Emoji 支持

`commit-workflow` 有完整的 gitmoji 映射表（13 对 type→emoji），如果用户有 emoji 约定的项目，可以识别并跟进。

**改法**：在 Stage 4 加入"如果项目 commit 历史使用 emoji，延续该风格"的规则。

### 5. [Low] 错误恢复补充

`release` by terrylica 的 Known Issues 章节是项目级 release 的经验库，包括 `git stash -u` 的 `.gitignore` 还原问题、mise depends 竞态、semantic-release `@semantic-release/git` 的 untracked file 问题等。这些虽然属于 `release` 专属，但"将失败经验文档化"的模式值得借鉴。

**改法**：在 Stage 8 末尾加一句"如发现可复现的失败模式，补充到 Known Issues"

### 6. [Medium] Pre-push 确认逻辑加强

当前 skill 要求"共享分支 / 生产分支"问用户确认。`publish-cli` 更进一步——push 前和 tag 前都显式 "Ask before pushing commits or tags"。

**改法**：在 Stage 6 确认点细化：**所有 push 到 shared branch 都需确认**，不只是 push 本身，还包括 tag creation。

---

## Source Notes

- Conventional Commits spec: 1.0.0, 16 MUST/SHALL 规则，全行业采纳
- `commit-workflow` (drvoss): 对 `caveman-commit` 的竞争产品——覆盖更多（pre-commit checks, diff split, emoji），但缺少版本管理、CHANGELOG、push 安全、出错恢复
- `publish-cli` (cline): 最完整的**单一语言/工具**发布流程 (npm CLI)，但在通用性和提交前阶段薄弱
- `release` (terrylica): 通用性较好 (mise + semantic-release)，但依赖特定工具栈，不适合非 Node/Python 项目
- `Benjaminsson` gist: 组织级 CI 标准化 + commitlint，不是 commit skill，但 CI 集成模式可参考
- Claude Code 官方 docs: 确认 skill 架构（personal/global/project 三层）、frontmatter fields、invocation 机制——我们的 skill 完全符合规范
