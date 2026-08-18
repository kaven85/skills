#!/usr/bin/env python3
"""Geometry and readability checks for uncompressed draw.io XML.

Usage: python validate-layout.py diagram.drawio [--page-margin 20] [--header-gap 12]
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Box:
    id: str; x: float; y: float; w: float; h: float; value: str; style: str; parent: str
    @property
    def r(self): return self.x + self.w
    @property
    def b(self): return self.y + self.h


def num(value, default=0.0):
    try: return float(value)
    except (TypeError, ValueError): return default


def style_value(style, key, default=None):
    m = re.search(r"(?:^|;)" + re.escape(key) + r"=([^;]+)", style or "")
    return m.group(1) if m else default


def is_lane(cell):
    return "swimlane" in (cell.get("style") or "")


def overlap(a, b):
    return max(a.x, b.x) < min(a.r, b.r) and max(a.y, b.y) < min(a.b, b.b)


def expanded(box, n):
    return Box(box.id, box.x-n, box.y-n, box.w+2*n, box.h+2*n, box.value, box.style, box.parent)


def segment_hits_box(x1, y1, x2, y2, box):
    # Liang–Barsky clipping: true for a segment crossing/touching a rectangle.
    dx, dy = x2-x1, y2-y1
    p, q = [-dx, dx, -dy, dy], [x1-box.x, box.r-x1, y1-box.y, box.b-y1]
    lo, hi = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0: return False
        else:
            t = qi / pi
            if pi < 0:
                if t > hi: return False
                lo = max(lo, t)
            else:
                if t < lo: return False
                hi = min(hi, t)
    return True


def label_text(value):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", html.unescape(value or ""))).strip()


def validate(path, page_margin=20, header_gap=12, safety=10):
    errors, warnings, report = [], [], {"manual_waypoints": 0, "pages": 0}
    try: root = ET.parse(path).getroot()
    except ET.ParseError as exc: return [f"XML parse error: {exc}"], warnings, report
    for diagram in root.findall("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None:
            warnings.append(f"[{diagram.get('name','page')}] compressed page skipped")
            continue
        report["pages"] += 1
        name = diagram.get("name", "page")
        cells = {c.get("id"): c for c in model.findall("./root/mxCell") if c.get("id")}
        local = {}
        for cid, c in cells.items():
            g = c.find("mxGeometry")
            if c.get("vertex") == "1" and g is not None:
                local[cid] = (num(g.get("x")), num(g.get("y")), num(g.get("width")), num(g.get("height")))
        def global_box(cid, seen=None):
            if cid not in local: return None
            seen = set() if seen is None else seen
            if cid in seen: return None
            seen.add(cid); x,y,w,h = local[cid]; parent = cells[cid].get("parent", "1")
            if parent in local:
                p = global_box(parent, seen)
                if p: x += p.x; y += p.y
            c = cells[cid]
            return Box(cid,x,y,w,h,c.get("value", ""),c.get("style", ""),parent)
        boxes = {cid: global_box(cid) for cid in local}
        boxes = {cid:b for cid,b in boxes.items() if b}
        lanes = [b for cid,b in boxes.items() if is_lane(cells[cid]) and cells[cid].get("parent") == "1"]
        lanes.sort(key=lambda b: b.y)
        for a,b in zip(lanes, lanes[1:]):
            if a.b + 40 > b.y:
                errors.append(f"[{name}] lanes '{a.id}' ({a.y:g}–{a.b:g}) and '{b.id}' ({b.y:g}–{b.b:g}) violate 40px vertical gap")
        for cid, box in boxes.items():
            cell = cells[cid]
            if is_lane(cell): continue
            parent = cell.get("parent")
            if parent in boxes and is_lane(cells[parent]):
                lane = boxes[parent]; start = num(style_value(lane.style, "startSize", "30"), 30)
                if box.y < lane.y + start + header_gap:
                    errors.append(f"[{name}] node '{cid}' intrudes lane '{parent}' header (top {box.y:g}, minimum {lane.y+start+header_gap:g})")
                if box.x < lane.x or box.r > lane.r or box.b > lane.b:
                    errors.append(f"[{name}] node '{cid}' exceeds parent lane '{parent}'")
            if box.x < page_margin or box.y < page_margin or box.r + page_margin > num(model.get("pageWidth"), 1169) or box.b + page_margin > num(model.get("pageHeight"), 827):
                warnings.append(f"[{name}] node '{cid}' is within {page_margin}px of or beyond page boundary")
            text = label_text(box.value)
            if (" / " in text or re.search(r"[\u4e00-\u9fff].*[A-Za-z]|[A-Za-z].*[\u4e00-\u9fff]", text)) and box.w < (240 if len(text)>36 else 200):
                errors.append(f"[{name}] bilingual node '{cid}' width {box.w:g} is below recommended minimum")
        non_lanes = [b for cid,b in boxes.items() if not is_lane(cells[cid])]
        for i,a in enumerate(non_lanes):
            for b in non_lanes[i+1:]:
                # Parent/child containment is intentional; unrelated node overlap is not.
                if a.parent == b.id or b.parent == a.id: continue
                if overlap(a,b): errors.append(f"[{name}] nodes '{a.id}' and '{b.id}' overlap")
        edge_labels = []
        for eid, edge in cells.items():
            if edge.get("edge") != "1": continue
            geom = edge.find("mxGeometry"); points = [] if geom is None else geom.findall(".//mxPoint[@as='points']")
            # draw.io points are normally mxArray/as=points; count every point conservatively.
            points = [] if geom is None else geom.findall(".//mxPoint")
            points = [p for p in points if p.get("as") not in ("sourcePoint", "targetPoint")]
            report["manual_waypoints"] += len(points)
            src, dst = boxes.get(edge.get("source")), boxes.get(edge.get("target"))
            if src and dst:
                # No points means renderer may route; check intended straight center path only when aligned.
                if not points and (abs((src.x+src.w/2)-(dst.x+dst.w/2)) < 1 or abs((src.y+src.h/2)-(dst.y+dst.h/2)) < 1):
                    x1,y1,x2,y2 = src.x+src.w/2,src.y+src.h/2,dst.x+dst.w/2,dst.y+dst.h/2
                    for oid, obstacle in boxes.items():
                        if oid not in (src.id,dst.id) and not is_lane(cells[oid]) and segment_hits_box(x1,y1,x2,y2,expanded(obstacle,safety)):
                            errors.append(f"[{name}] straight edge '{eid}' crosses node '{oid}' (including {safety}px safety margin)")
                text = label_text(edge.get("value"))
                if text and (" / " in text) and max(abs(src.x-dst.x),abs(src.y-dst.y)) < 160:
                    errors.append(f"[{name}] bilingual edge label '{eid}' lacks 160px routing space")
                if text:
                    # Draw.io normally places an un-offset edge label near the route midpoint.
                    # This conservative estimate catches the common case; custom offsets still
                    # require the exported-preview QA step.
                    width = max(60, min(320, len(text) * 8 + 20))
                    label = Box(eid, (src.x+src.w/2+dst.x+dst.w/2-width)/2,
                                (src.y+src.h/2+dst.y+dst.h/2-22)/2,
                                width, 22, text, "", "")
                    edge_labels.append(label)
                    for oid, obstacle in boxes.items():
                        if oid not in (src.id, dst.id) and not is_lane(cells[oid]) and overlap(label, obstacle):
                            errors.append(f"[{name}] edge label '{eid}' overlaps node '{oid}'")
                    for lane in lanes:
                        header = Box(lane.id, lane.x, lane.y, lane.w,
                                     num(style_value(lane.style, "startSize", "30"), 30), "", "", "")
                        if overlap(label, header):
                            errors.append(f"[{name}] edge label '{eid}' overlaps lane header '{lane.id}'")
        for i, label in enumerate(edge_labels):
            for other in edge_labels[i+1:]:
                if overlap(label, other):
                    errors.append(f"[{name}] edge labels '{label.id}' and '{other.id}' overlap")
    return errors, warnings, report


def main():
    p = argparse.ArgumentParser(); p.add_argument("diagram"); p.add_argument("--page-margin", type=float, default=20); p.add_argument("--header-gap", type=float, default=12)
    a = p.parse_args(); errors,warnings,report = validate(Path(a.diagram),a.page_margin,a.header_gap)
    print(f"Layout report: pages={report['pages']}; manual-waypoints={report['manual_waypoints']}")
    for w in warnings: print("WARNING:",w)
    for e in errors: print("ERROR:",e)
    print("PASS — layout checks passed." if not errors else f"FAIL — {len(errors)} layout error(s).")
    return 0 if not errors else 1
if __name__ == "__main__": sys.exit(main())
