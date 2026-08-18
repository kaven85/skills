#!/usr/bin/env bash
# Optional local preview: render ```mermaid blocks to SVG/PNG for visual QA.
# The styled Mermaid code is the deliverable; this script only checks it.
#
# Requires mermaid-cli:  npm i -g @mermaid-js/mermaid-cli
#
# usage: render-preview.sh <file.mmd|file.md> <out.svg|out.png> [theme]
#   .mmd  -> renders the single diagram
#   .md   -> extracts every ```mermaid block; outputs out.svg, out-2.svg, ...

set -euo pipefail

input="${1:?usage: render-preview.sh <file.mmd|file.md> <out.svg|out.png> [theme]}"
output="${2:?missing output path (.svg or .png)}"
theme="${3:-default}"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mmdc not found. Install with: npm i -g @mermaid-js/mermaid-cli" >&2
  exit 2
fi

render_one() {
  local src="$1" dst="$2"
  mmdc -i "$src" -o "$dst" -t "$theme" -b transparent --quiet
  echo "render: OK -> $dst"
}

if [[ "$input" == *.mmd ]]; then
  render_one "$input" "$output"
  exit 0
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

# Split fenced mermaid blocks into block-1.mmd, block-2.mmd, ...
awk -v dir="$tmpdir" '
  /^```mermaid[[:space:]]*$/ { n++; out = sprintf("%s/block-%d.mmd", dir, n); next }
  /^```[[:space:]]*$/        { out = ""; next }
  out != ""                 { print > out }
' "$input"

count="$(find "$tmpdir" -name 'block-*.mmd' | wc -l | tr -d ' ')"
if [[ "$count" == "0" ]]; then
  echo "no mermaid blocks found in $input" >&2
  exit 1
fi

base="${output%.*}"
ext="${output##*.}"
for src in "$tmpdir"/block-*.mmd; do
  n="${src##*block-}"; n="${n%.mmd}"
  if [[ "$count" == "1" ]]; then
    render_one "$src" "$output"
  else
    render_one "$src" "${base}-${n}.${ext}"
  fi
done
