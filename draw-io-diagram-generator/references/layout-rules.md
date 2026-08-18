# Layout rules

Plan semantic lanes, groups, nodes, and dimensions before writing XML. Child geometry is relative to its parent; calculate global coordinates recursively for every collision, routing, and bounds check.

Use a 40px minimum vertical gap between top-level swimlanes. A child must start at least `startSize + 12px` below its lane top. Keep ordinary siblings 40px apart, business groups 50–80px apart, and Port-to-Adapter rows 50px apart. Reserve 20px at lane bottoms and page edges.

Size the canvas from content, not a fixed A4 default. When it expands, update page dimensions, lane widths, title centering, right margin, and connection projections. Bilingual nodes are at least 200px wide, or 240px for longer descriptions.
