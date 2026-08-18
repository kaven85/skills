#!/usr/bin/env python3
"""Print edges containing hand-authored mxPoint waypoints."""
import sys, xml.etree.ElementTree as ET
from pathlib import Path
root=ET.parse(Path(sys.argv[1])).getroot(); count=0
for d in root.findall('diagram'):
 for c in d.findall('.//mxCell[@edge="1"]'):
  pts=[p for p in c.findall('.//mxPoint') if p.get('as') not in ('sourcePoint','targetPoint')]
  if pts: count+=len(pts); print(f"{d.get('name','page')}: {c.get('id')} has {len(pts)} manual waypoint(s)")
print(f"manual-waypoints={count}")
