# skills

Personal agent skill collection.

## Skills

| Skill | Description |
|---|---|
| [commit-release](commit-release/) | Orchestrate the full code submission pipeline: inspect changes, check version/CHANGELOG, stage, run tests, write commit message, push, and… |
| [draw-io-diagram-generator](draw-io-diagram-generator/) | Use when creating, editing, or generating draw.io diagram files (.drawio, .drawio.svg, .drawio.png). Covers mxGraph XML authoring, shape li… |
| [mermaid-diagram-generator](mermaid-diagram-generator/) | Use when creating, editing, or styling Mermaid diagrams inside Markdown (```mermaid fenced blocks or .mmd files) so they render more beauti… |

## Maintenance

`README.md` 的技能表格由 `scripts/gen_readme.py` 自动生成，数据来源是各技能
`SKILL.md` 的 frontmatter（`name` / `description`）。push 到 `main` 且
`*/SKILL.md` 发生变化时，GitHub Action 会自动重建并提交；本地也可以手动运行：

```bash
python3 scripts/gen_readme.py
```
