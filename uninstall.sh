#!/bin/bash
# Removes the menu entry, keybind and launcher. Leaves the repo alone.
set -euo pipefail
TAG="im-a-hacker-mommy"
MENU="$HOME/.config/omarchy/extensions/omarchy-menu.jsonc"
BINDINGS="$HOME/.config/hypr/bindings.lua"

rm -f "$HOME/.local/bin/do-a-hacking"
if [[ -f "$MENU" ]]; then
  python3 - "$MENU" "$TAG" <<'PY'
import sys
path, tag = sys.argv[1:3]
marker = "// " + tag
lines = open(path, encoding="utf-8").read().split("\n")
out, drop_next = [], False
for line in lines:
    stripped = line.strip()
    if drop_next:
        drop_next = False
        if stripped.startswith('"'):
            continue  # the row that followed a tag on its own line
    if stripped == marker:
        drop_next = True  # tag on its own line: the row is the next line
        continue
    if stripped.endswith(marker):
        continue  # tag at the end of the row itself
    out.append(line)
# the removed row may have been the last one: drop the comma now left dangling
close = max((i for i, l in enumerate(out) if l.strip() == "}"), default=None)
if close is not None:
    for i in range(close - 1, -1, -1):
        stripped = out[i].strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped.endswith(","):
            out[i] = out[i].rstrip()[:-1]
        break
if out != lines:
    open(path, "w", encoding="utf-8").write("\n".join(out))
PY
fi
[[ -f "$BINDINGS" ]] && sed -i "/^-- >>> $TAG >>>\$/,/^-- <<< $TAG <<<\$/d" "$BINDINGS"
hyprctl reload >/dev/null 2>&1 || true
echo "  uninstalled. you were never a hacker. the kettle is safe."
