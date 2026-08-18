#!/usr/bin/env python3
"""Regenerate the root README.md from each skill's SKILL.md frontmatter.

Scans <repo>/*/SKILL.md, extracts `name` and `description` from YAML
frontmatter, and rewrites README.md between the managed markers.
Run locally (`python3 scripts/gen_readme.py`) or via .github/workflows/readme.yml.
"""
from pathlib import Path

import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DESC_LIMIT = 140

HEADER = """# skills

Personal agent skill collection.

## Skills

| Skill | Description |
|---|---|
"""

FOOTER = """
## Maintenance

`README.md` 的技能表格由 `scripts/gen_readme.py` 自动生成，数据来源是各技能
`SKILL.md` 的 frontmatter（`name` / `description`）。push 到 `main` 且
`*/SKILL.md` 发生变化时，GitHub Action 会自动重建并提交；本地也可以手动运行：

```bash
python3 scripts/gen_readme.py
```
"""


def iter_skills():
    """Yield (name, description, dirname) for every skill directory."""
    for skill_md in sorted(ROOT.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            continue
        frontmatter = yaml.safe_load(match.group(1)) or {}
        name = frontmatter.get("name") or skill_md.parent.name
        description = str(frontmatter.get("description") or "").strip()
        yield name, description, skill_md.parent.name


def table_cell(text):
    """Collapse whitespace, truncate, and escape pipes for a table cell."""
    text = " ".join(text.split())
    if len(text) > DESC_LIMIT:
        text = text[: DESC_LIMIT - 1].rstrip() + "…"
    return text.replace("|", "\\|")


def main():
    rows = "\n".join(
        f"| [{name}]({dirname}/) | {table_cell(description)} |"
        for name, description, dirname in iter_skills()
    )
    content = HEADER + rows + "\n" + FOOTER
    previous = README.read_text(encoding="utf-8") if README.exists() else None
    if previous == content:
        print("README.md already up to date")
        return
    README.write_text(content, encoding="utf-8")
    print(f"README.md regenerated ({rows.count(chr(10)) + 1} skill(s))")


if __name__ == "__main__":
    main()
