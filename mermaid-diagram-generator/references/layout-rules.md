# Layout and Readability Rules

Mermaid gives no coordinate control; readability comes from budgets, direction, ordering, and restraint. Contents:

- Budgets
- Direction strategy
- Crossing reduction
- Labels
- Lanes
- Emphasis
- Iterating
- When Mermaid is the wrong tool

## Budgets

- ≤15 nodes and ≤25 edges per diagram. A flowchart past that is a system diagram — split it.
- ≤4 subgraph lanes per diagram, ≤6 children per lane.
- Two small diagrams (overview + detail) beat one dense diagram every time. Overview shows lanes and their relationships; detail zooms into one lane.

## Direction strategy

| Content | Direction |
|---|---|
| Pipeline / request path / data flow | `flowchart LR` |
| Wide tree or hierarchy | `LR` (long labels read better horizontally) |
| Decision flow / approval process | `flowchart TD` |
| Timeline-like progression | `LR`, or use `timeline` |

Set `direction` inside a subgraph to orient its interior independently of the outer flow.

## Crossing reduction

- Define edges in topological order following the main flow. Mermaid's ranker respects definition order.
- Group edge definitions by source lane.
- Use invisible links (`A ~~~ B`) to pin two nodes to the same rank or to nudge spacing.
- A hub node with >5 edges: connect it via a `neutral`-styled bus node (e.g. `MQ[/"Kafka"/]`) instead of fanning edges.
- ELK renderer (`%%{init: {"flowchart": {"defaultRenderer": "elk"}}}%%`) routes dense graphs far better, but support varies by renderer — verify on the target before relying on it.

## Labels

- Node labels ≤12 half-width chars (≤8 Chinese chars). Push detail into the surrounding prose.
- Edge labels ≤8 chars. Long explanations belong in a `Note` (sequence) or the text, not on an arrow.
- Bilingual labels: `A["资产登记<br/>Asset Registry"]`. Reserve bilingual text for architecture nodes only.
- Emoji act as portable icons: 🌐 📱 🔐 🗄️ ⛓️ 💱 ✅ ❌. One per node, leading.
- The diagram title belongs in the Markdown heading above the block, not inside Mermaid.

## Lanes

- Lane order is reading order; inter-lane edges should flow one way.
- Tint lane fills faint (10–15% saturation of the class stroke color); never saturated fills behind nodes.
- Lane titles ≤6 chars; they are orientation aids, not documentation.

## Emphasis

- One accent per diagram: a `linkStyle` critical path, or a single `ink`/`warning` node. Two accents compete.
- `classDef default ...` for a uniform base, then semantic classes only where they mean something.
- Dashed edges for anything future/optional/async — readers learn the convention after one diagram if you are consistent.

## Iterating

- Change one thing per pass (direction, then spacing, then order). Auto-layout shifts everything at once.
- If a diagram needs more than ~3 invisible-link hacks, the structure is wrong — split the diagram.

## When Mermaid is the wrong tool

Switch to the `draw-io-diagram-generator` skill when any of these hold:

- >25 nodes with dense cross-links (network topology, BPMN with pools)
- Pixel-exact placement or alignment requirements (exec decks, print)
- Branded exports (custom fonts, logos, exact hex backgrounds in PNG/PDF)
- The user needs to drag-edit the diagram afterward

Say so explicitly when handing off: "this diagram has outgrown Mermaid's auto-layout; here is a draw.io version instead."
