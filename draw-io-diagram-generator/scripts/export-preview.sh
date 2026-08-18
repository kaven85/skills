#!/usr/bin/env bash
# Export a preview with the draw.io desktop CLI when installed.
set -euo pipefail
if [ "$#" -ne 2 ]; then echo "Usage: $0 input.drawio output.png|svg" >&2; exit 2; fi
if command -v drawio >/dev/null 2>&1; then
  if drawio --export --format "${2##*.}" --output "$2" "$1"; then exit 0; fi
  echo "Draw.io CLI export failed; visual render check NOT RUN." >&2; exit 3
fi
if [ -x "/Applications/draw.io.app/Contents/MacOS/draw.io" ]; then
  if "/Applications/draw.io.app/Contents/MacOS/draw.io" --export --format "${2##*.}" --output "$2" "$1"; then exit 0; fi
  echo "Draw.io app CLI export failed; visual render check NOT RUN." >&2; exit 3
fi
echo "Draw.io CLI unavailable; visual render check NOT RUN." >&2
exit 3
