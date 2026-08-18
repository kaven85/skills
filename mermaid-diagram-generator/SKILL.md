---
name: mermaid-diagram-generator
description: Use when creating, editing, or styling Mermaid diagrams inside Markdown (```mermaid fenced blocks or .mmd files) so they render more beautifully. Covers flowcharts, system architecture (subgraph lanes), sequence, ER, UML class, state, mindmap, timeline, gantt, quadrant, sankey, and xychart diagrams; theming via %%{init}%% directives and themeVariables; semantic classDef color palettes; linkStyle edge styling; layout and readability rules; renderer compatibility (GitHub, GitLab, Obsidian, VS Code, Notion, Typora, Codex app); and syntax validation with the mermaid module or mermaid-cli. Trigger phrases include "mermaid", "画个流程图/架构图/时序图/ER图", "在 md/markdown 里画图", "美化这个 mermaid 图", "让 mermaid 更好看".
---

# Mermaid Diagram Generator

Generate Mermaid diagrams that render immediately in Markdown viewers (GitHub, GitLab, Obsidian, VS Code, Notion, Typora, Codex app) and look designed rather than default. The deliverable is styled Mermaid code, not an exported image. Mermaid auto-layouts everything — beauty comes from a disciplined theme + palette + shape system, not from coordinates.

## 1. Supported Diagram Types

| Diagram Type | Keyword | Styled Example |
|---|---|---|
| Flowchart | `flowchart` | `references/diagram-recipes.md` |
| System Architecture (lanes) | `flowchart` + `subgraph` | `references/diagram-recipes.md` |
| Sequence | `sequenceDiagram` | `references/diagram-recipes.md` |
| ER | `erDiagram` | `references/diagram-recipes.md` |
| UML Class | `classDiagram` | `references/diagram-recipes.md` |
| State | `stateDiagram-v2` | `references/diagram-recipes.md` |
| Mindmap | `mindmap` | `references/diagram-recipes.md` |
| Timeline | `timeline` | `references/diagram-recipes.md` |
| Gantt | `gantt` | `references/diagram-recipes.md` |
| Quadrant / Sankey / XY chart | `quadrantChart` / `sankey-beta` / `xychart-beta` | `references/diagram-recipes.md` |

Renderer note: GitHub, Obsidian, and current VS Code extensions run Mermaid 11.x. `-beta` types, generic `@{shape:}` syntax, and ELK layout may fail on older or embedded renderers. When the target renderer is unknown, prefer core types and classic shape syntax.

## 2. Agent Workflow

Follow these steps in order for every diagram task.

### Step 1 — Understand the Request

Infer: diagram type, entities/actors, relationships and direction, target Markdown file, and the target renderer if known. Infer the most sensible type from context ("下单流程" → flowchart, "表结构" → ER, "接口调用顺序" → sequence).

### Step 2 — Build a Semantic Model (required for architecture and complex flows)

Before writing Mermaid, model explicitly: lanes → groups → nodes with roles → relationship types. Classify every edge as call, data flow, dependency, async message, or future/optional. This classification determines colors (semantic classDefs), lanes (subgraphs), and line styles (solid / dashed / thick). Implementation alternatives branch from a common port node; never draw adapter-to-adapter arrows unless the flow is genuinely synchronization.

### Step 3 — Apply the Theme

Start every diagram with the canonical init directive and classDef palette from §3, unless the user already has a house style. Additional presets (minimal, dark): `references/theme-presets.md`.

### Step 4 — Author the Diagram

Follow the recipe for the type (§4 or `references/diagram-recipes.md`) and the layout rules (`references/layout-rules.md`). Quote every label. Assign classes inline (`:::primary`) or with `class` statements.

### Step 5 — Validate and Deliver

1. Syntax-validate: `node scripts/validate-mermaid.mjs <file.md>` — validates every ```mermaid block in the file. Install `mermaid` + `jsdom` in the current project; the script prints an install hint if mermaid is missing.
2. Optional visual QA: when mermaid-cli (`mmdc`) is installed, `scripts/render-preview.sh <file.md> preview.svg` renders a local preview. This is a check, not the deliverable — the user previews in their own Markdown viewer.
3. If no validation tool is available, record `validate: NOT RUN` and never claim the diagram was verified.
4. Deliver as a ```mermaid fenced block inside the target `.md` file (or a standalone `.mmd` file when requested).

## 3. The Beauty System (apply by default)

### 3.1 Canonical Init Directive

Place as the FIRST line inside the mermaid block. Keep it single-line valid JSON.

```
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#64748b", "primaryTextColor": "#1f2937", "edgeLabelBackground": "#ffffff", "clusterBkg": "#f8fafc", "clusterBorder": "#cbd5e1"}, "flowchart": {"curve": "basis", "nodeSpacing": 45, "rankSpacing": 55}}}%%
```

- Always `theme: base` + explicit `themeVariables`; named themes (`forest`, `neutral`) fight custom palettes.
- `curve`: `basis` (smooth) for flows; `linear` (straight segments) for architecture diagrams.
- Raise `nodeSpacing`/`rankSpacing` above defaults (25/50) to reduce crowding.

### 3.2 Semantic classDef Palette

Mirrors the draw.io house palette so Mermaid and .drawio artifacts look like one family.

```
classDef primary  fill:#dae8fc,stroke:#6c8ebf,stroke-width:1.5px,color:#1f2937;
classDef success  fill:#d5e8d4,stroke:#82b366,stroke-width:1.5px,color:#1f2937;
classDef warning  fill:#fff2cc,stroke:#d6b656,stroke-width:1.5px,color:#1f2937;
classDef danger   fill:#f8cecc,stroke:#b85450,stroke-width:1.5px,color:#1f2937;
classDef neutral  fill:#f5f5f5,stroke:#666666,stroke-width:1.2px,color:#374151;
classDef external fill:#e1d5e7,stroke:#9673a6,stroke-width:1.5px,color:#1f2937;
```

| Purpose | Class |
|---|---|
| Primary / info / current service | `primary` |
| Start / success / healthy state | `success` |
| Decision / gateway / attention | `warning` |
| Data store / end-state / risk | `danger` |
| Infra / queue / low-emphasis | `neutral` |
| Third-party / external system | `external` |

Assign with `A["Label"]:::primary` or `class A,B primary`. `classDef default ...` restyles every node at once.

### 3.3 Shapes (classic syntax, works everywhere)

```
A["rect"]   A("round rect")   A(["stadium"])   A{"decision"}   A{{"hexagon"}}
A[("cylinder db")]   A[["subroutine"]]   A[/"parallelogram"/]   A[\"trapezoid"\]
A(("circle"))   A>"flag"]
```

Shape communicates role: stadium for start/end, diamond for decision, cylinder for data store, subroutine for external call. Mermaid 11.3+ adds generic shapes (`A@{shape: doc}`) — verify renderer version first.

### 3.4 Edges

```
A --> B   A --- B   A -.-> B   A ==> B   A ~~~ B   A -->|label| B   A <--> B   A --o B
```

- `~~~` is an invisible layout link — the main tool for taming auto-layout.
- Style edges by 0-based definition order: `linkStyle 0,2 stroke:#b85450,stroke-width:2.5px;`
- Semantics: solid = call/flow, `-.->` = optional/future/async, `==>` = critical path.

### 3.5 Subgraph Lanes

```
subgraph SVC["服务层"]
  direction LR
  A["订单服务"]:::primary
end
style SVC fill:#f0fdf4,stroke:#82b366,stroke-width:1px,color:#1f4427
```

- `direction` affects only the subgraph interior.
- Tint each lane with a faint shade of its semantic stroke color.
- Budget: ≤4 lanes per diagram, ≤6 children per lane.

## 4. Compact Recipes

Complete themed versions live in `references/diagram-recipes.md`.

### Flowchart with Decision

```
flowchart TD
  START(["开始"]):::success --> INPUT["输入订单参数"]:::primary
  INPUT --> CHECK{"库存充足?"}:::warning
  CHECK -->|"是"| PAY["扣减库存并支付"]:::primary
  CHECK -->|"否"| NOTIFY["通知缺货"]:::danger
  PAY --> DONE(["完成"]):::success
  NOTIFY --> DONE
```

### Architecture with Lanes

```
flowchart LR
  subgraph CLIENT["客户端"]
    direction LR
    WEB["🌐 Web 控制台"]:::primary
    APP["📱 移动 App"]:::primary
  end
  GW["API 网关"]:::warning
  subgraph DATA["数据层"]
    direction LR
    DB[("PostgreSQL")]:::danger
  end
  WEB --> GW
  APP --> GW
  GW --> DB
  style CLIENT fill:#f0f7ff,stroke:#6c8ebf,color:#1e3a5f
  style DATA fill:#fef2f2,stroke:#b85450,color:#5f2120
```

### Sequence with alt + note

```
sequenceDiagram
  autonumber
  participant U as 👤 用户
  participant A as 🔐 认证服务
  U->>A: POST /auth/login
  activate A
  alt 校验通过
    A-->>U: 200 + JWT
  else 校验失败
    A-->>U: 401 Unauthorized
  end
  deactivate A
  Note over U,A: Token 有效期 2 小时
```

### ER with Keys

```
erDiagram
  USER ||--o{ ORDER : "发起"
  USER {
    bigint id PK
    varchar name "用户姓名"
  }
  ORDER {
    bigint id PK
    bigint user_id FK
    decimal total_amount
  }
```

## 5. Layout and Readability Rules (summary)

Full rules: `references/layout-rules.md`. Essentials:

- Budget ≤15 nodes and ≤25 edges per diagram; split larger systems into overview + detail diagrams.
- Pipelines and wide trees → `flowchart LR`; decision flows → `TD`.
- One idea per diagram; the title belongs in the Markdown heading, not inside Mermaid.
- Node labels ≤12 chars (Chinese ≤8); edge labels ≤8; bilingual labels joined with `<br/>`.
- Reduce crossings via edge definition order and invisible links; never fight auto-layout — split the diagram instead.
- `linkStyle` only for emphasis (critical path, failure path).

## 6. Syntax Gotchas

- ALWAYS quote labels containing spaces, parens, colons, or Chinese punctuation: `A["调用 (retry)"]`.
- Edge labels: `A -->|"是"| B` pipe syntax is universally supported.
- Comments are `%% text %%`, never `#`.
- The init directive must be the first line; keep it single-line JSON.
- Node ids: letters/digits/underscore only — Chinese text goes in the quoted label, never the id.
- Full-width punctuation is fine inside quotes and breaks unquoted labels.
- `linkStyle` indexes count every edge in definition order, including edges inside subgraphs.
- `flowchart`, not legacy `graph` — the newer engine renders better.

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| Parse error near a label | Quote the label; check for full-width brackets outside quotes |
| classDef has no effect | Class name typo; correct inline form is `ID["label"]:::class` |
| Theme ignored | init directive not on first line, or invalid JSON |
| Diagram too wide / cramped | Switch LR↔TD, raise nodeSpacing, or split into two diagrams |
| linkStyle colors the wrong edge | Recount 0-based edge order, including subgraph-internal edges |
| `-beta` diagram fails on GitHub | Renderer too old — use a core type or accept mermaid.live-only rendering |
| Emoji missing on a platform | Emoji are portable; Font Awesome `fa:` icons only render where FA is registered |
| `class 中文名 xxx` fails in stateDiagram-v2 | The standalone `class` statement needs ASCII ids — attach inline (`中文名:::xxx`) or declare `state "中文名" as ID` first |
| sankey-beta rejects Chinese labels | sankey-beta is ASCII-only (no CJK, no quotes) — use English/pinyin labels and explain in prose |

## 8. Validation Checklist

- [ ] init directive on first line, valid JSON, `theme: base`
- [ ] every label quoted; ids alphanumeric
- [ ] semantic classDefs defined once and used consistently
- [ ] every edge classified: solid / dashed / thick / invisible
- [ ] node, edge, and lane budgets respected
- [ ] `node scripts/validate-mermaid.mjs` passed (or marked NOT RUN)

## 9. Output Format

When delivering a diagram, always provide:

1. The ```mermaid block written into the target `.md` (or `.mmd`) file
2. A one-sentence summary of what the diagram shows
3. Validation status (validator run? marked NOT RUN?)
4. Where it renders (GitHub / Obsidian / VS Code / Notion / Typora / Codex app)
5. If the diagram outgrew Mermaid (dense cross-links, pixel-exact placement needed), say so and offer the `draw-io-diagram-generator` skill as the escape hatch

## 10. References

| File | Contents |
|---|---|
| `references/theme-presets.md` | Ready-to-paste init directives: Semantic Light (default), Slate Minimal, Dark; per-diagram themeVariables cheat sheet |
| `references/diagram-recipes.md` | Complete styled examples for all supported diagram types |
| `references/layout-rules.md` | Node budgets, direction strategy, crossing reduction, label rules, when Mermaid is the wrong tool |
| `scripts/validate-mermaid.mjs` | Syntax-validate every ```mermaid block in a `.md` (or a `.mmd`) via `mermaid.parse` |
| `scripts/render-preview.sh` | Optional local preview via mermaid-cli (QA only; the deliverable is the Mermaid code itself) |
| `scripts/README.md` | Script install, usage, examples, behavior, and exit codes |
