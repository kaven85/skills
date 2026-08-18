# Mermaid Scripts

Utility scripts for syntax-checking and previewing Mermaid diagrams inside Markdown (mermaid fenced blocks) or standalone `.mmd` files. The styled Mermaid code is the deliverable — these scripts are QA only.

## Requirements

- Node.js 16+ (ESM, top-level `await`)
- The `mermaid` npm module, resolved in this order:
  1. `$MERMAID_MODULE` — path to a mermaid package dir (resolved to its dist bundle) or `.mjs` bundle
  2. `mermaid` resolvable from the current working directory
- `jsdom` for diagram types that sanitize labels (flowchart, class, state, mindmap, gantt, and charts)
- `render-preview.sh` additionally requires mermaid-cli (`mmdc`)

## Scripts

### `validate-mermaid.mjs`

Syntax-validates every mermaid fenced block in a `.md` file, or a whole `.mmd` file, via `mermaid.parse`.

**Usage**

```bash
node scripts/validate-mermaid.mjs <file.md|file.mmd> [...]
```

**Examples**

```bash
# Validate all mermaid blocks in a doc
node scripts/validate-mermaid.mjs docs/architecture.md

# Validate a standalone diagram file
node scripts/validate-mermaid.mjs diagrams/pipeline.mmd

# Validate several files at once
node scripts/validate-mermaid.mjs docs/*.md
```

**Install validation dependencies**

```bash
npm i -D mermaid jsdom              # in the current project, or
npm i -g mermaid && npm i -D jsdom
export MERMAID_MODULE="$(npm root -g)/mermaid"
```

**Behavior**

| Input | Behavior |
|---|---|
| `.md` | Extracts every mermaid fenced block, validates each with `mermaid.parse` |
| `.mmd` | Validates the whole file as one diagram |

jsdom shim: when `globalThis.document` is undefined, the script resolves `jsdom` from the current working directory and installs browser globals before importing mermaid. Without `jsdom`, sequence and ER may still parse, but diagram types that sanitize labels fail.

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Every block parsed |
| `1` | One or more parse failures (first 6 lines of each error printed to stderr) |
| `2` | Usage error (no files given) or `mermaid` module not found |

A `.md` with zero mermaid blocks prints `no mermaid blocks found` and still exits `0`.

---

### `render-preview.sh`

Optional local preview: renders mermaid blocks to SVG/PNG via mermaid-cli. QA only — the deliverable is the Mermaid code itself.

**Usage**

```bash
scripts/render-preview.sh <file.mmd|file.md> <out.svg|out.png> [theme]
```

**Examples**

```bash
# Render a standalone .mmd to SVG
scripts/render-preview.sh diagrams/pipeline.mmd preview.svg

# Render every block in a .md; multiple blocks -> preview-1.svg, preview-2.svg, ...
scripts/render-preview.sh docs/architecture.md preview.svg

# Use a named mermaid theme (default: default)
scripts/render-preview.sh diagrams/pipeline.mmd preview.png dark
```

**Behavior**

| Input | Output |
|---|---|
| `.mmd` | Single render to `<out>` |
| `.md`, exactly 1 block | Single render to `<out>` |
| `.md`, N blocks | `<base>-1.<ext>`, `<base>-2.<ext>`, … `<base>-N.<ext>` |

Renders with a transparent background (`-b transparent`).

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Rendered |
| `1` | No mermaid blocks found in the `.md` input |
| `2` | `mmdc` not installed |

**Requirements**

```bash
npm i -g @mermaid-js/mermaid-cli
```

---

## Common Workflows

### Validate before delivering

```bash
node scripts/validate-mermaid.mjs docs/*.md
```

### Validate + visual check

```bash
node scripts/validate-mermaid.mjs docs/architecture.md
scripts/render-preview.sh docs/architecture.md preview.svg
```

If neither tool is available, record the diagram as `validate: NOT RUN` (SKILL.md §2 Step 5) and never claim it was verified.
