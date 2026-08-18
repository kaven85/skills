# Routing rules

Classify every relationship first: call, data flow, dependency, implementation/replacement, optional extension, or synchronization. Alternatives implementing the same Port branch from that Port; never connect one alternative adapter to another as if it synchronized.

Route in this order: vertical straight line, horizontal straight line, one bend, then multi-bend only with an explicit reason. Move nodes before adding waypoints. For a horizontal Port bus, project to a target with `exitX = (targetCenterX - sourceX) / sourceWidth`; leave all system-architecture edges without manual `mxPoint` waypoints whenever possible. Check each segment against every non-endpoint node expanded by 10–20px.

Treat edge labels as boxes. Do not use long labels on short edges; reserve 100–160px for bilingual labels and keep them off lane headers, nodes, and other labels.
