# Theme Presets

Ready-to-paste init directives and classDef sets. Contents:

- Semantic Light (default, mirrors the draw.io house palette)
- Slate Minimal (grayscale, for reports and wikis)
- Dark (for dark-mode docs and slides)
- themeVariables cheat sheet (flowchart, sequence, gantt, ER)

All presets assume `theme: base` (or `theme: dark` for Dark). The init directive must be the first line inside the mermaid block, single-line valid JSON. Blocks below are wrapped for readability — join the init directive onto one line when pasting.

## 1. Semantic Light (default)

```
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#64748b", "primaryTextColor": "#1f2937", "edgeLabelBackground": "#ffffff", "clusterBkg": "#f8fafc", "clusterBorder": "#cbd5e1"}, "flowchart": {"curve": "basis", "nodeSpacing": 45, "rankSpacing": 55}}}%%

classDef primary  fill:#dae8fc,stroke:#6c8ebf,stroke-width:1.5px,color:#1f2937;
classDef success  fill:#d5e8d4,stroke:#82b366,stroke-width:1.5px,color:#1f2937;
classDef warning  fill:#fff2cc,stroke:#d6b656,stroke-width:1.5px,color:#1f2937;
classDef danger   fill:#f8cecc,stroke:#b85450,stroke-width:1.5px,color:#1f2937;
classDef neutral  fill:#f5f5f5,stroke:#666666,stroke-width:1.2px,color:#374151;
classDef external fill:#e1d5e7,stroke:#9673a6,stroke-width:1.5px,color:#1f2937;
```

Lane tints (subgraph `style`): `#f0f7ff/#6c8ebf` (client), `#fffbeb/#d6b656` (gateway), `#f0fdf4/#82b366` (services), `#fef2f2/#b85450` (data), `#faf5ff/#9673a6` (external).

## 2. Slate Minimal

For research reports and wikis where color should be sparse. One accent color maximum.

```
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#94a3b8", "primaryColor": "#ffffff", "primaryBorderColor": "#64748b", "primaryTextColor": "#0f172a", "clusterBkg": "#f8fafc", "clusterBorder": "#e2e8f0", "edgeLabelBackground": "#ffffff"}, "flowchart": {"curve": "linear", "nodeSpacing": 50, "rankSpacing": 60}}}%%

classDef ink    fill:#1e293b,stroke:#0f172a,stroke-width:1.5px,color:#f8fafc;
classDef panel  fill:#ffffff,stroke:#64748b,stroke-width:1.2px,color:#0f172a;
classDef accent fill:#e0e7ff,stroke:#6366f1,stroke-width:1.5px,color:#1e1b4b;
classDef muted  fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#475569;
```

Usage: `ink` for the single most important node, `accent` for the decision/focus, `panel` default, `muted` for infra.

## 3. Dark

For dark-mode documentation. Test on the target renderer — some viewers force their own dark theme and ignore these values.

```
%%{init: {"theme": "dark", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#94a3b8", "primaryTextColor": "#e2e8f0", "clusterBkg": "#0f172a", "clusterBorder": "#334155", "edgeLabelBackground": "#1e293b"}, "flowchart": {"curve": "basis", "nodeSpacing": 45, "rankSpacing": 55}}}%%

classDef primary  fill:#1d4ed8,stroke:#93c5fd,stroke-width:1.5px,color:#eff6ff;
classDef success  fill:#15803d,stroke:#86efac,stroke-width:1.5px,color:#f0fdf4;
classDef warning  fill:#a16207,stroke:#fde047,stroke-width:1.5px,color:#fefce8;
classDef danger   fill:#b91c1c,stroke:#fca5a5,stroke-width:1.5px,color:#fef2f2;
classDef neutral  fill:#334155,stroke:#94a3b8,stroke-width:1.2px,color:#e2e8f0;
classDef external fill:#7e22ce,stroke:#d8b4fe,stroke-width:1.5px,color:#faf5ff;
```

## 4. themeVariables Cheat Sheet

Common (all diagram types):

| Key | Effect |
|---|---|
| `fontFamily` / `fontSize` | Typography. Use system font stacks |
| `primaryColor` / `primaryBorderColor` / `primaryTextColor` | Default node fill / border / text |
| `lineColor` | Edge and arrow color |
| `textColor` | Standalone text color |
| `clusterBkg` / `clusterBorder` | Subgraph lane fill / border |
| `edgeLabelBackground` | Backing fill behind edge labels (set to background color) |

Sequence diagrams:

| Key | Effect |
|---|---|
| `actorBkg` / `actorBorder` / `actorTextColor` | Participant boxes |
| `actorLineColor` | Lifelines |
| `signalColor` / `signalTextColor` | Message arrows / message text |
| `activationBkg` / `activationBorder` | Activation boxes |
| `noteBkg` / `noteBorder` / `noteTextColor` | Notes |
| `loopLineColor` | loop/alt/opt frame lines |
| `sequenceNumberColor` | `autonumber` badge text |

Gantt:

| Key | Effect |
|---|---|
| `gridColor` | Grid lines |
| `sectionBkgColor` / `altSectionBkgColor` | Alternating section bands |
| `taskBkgColor` / `taskBorderColor` | Default task bars |
| `activeTaskBkgColor` / `doneTaskBkgColor` / `critBkgColor` | State-specific bars |
| `todayLineColor` | Today marker |

ER and class diagrams inherit the primary/secondary family; per-node classDefs are not supported — keep these diagrams on a clean base theme and let structure carry the design.
