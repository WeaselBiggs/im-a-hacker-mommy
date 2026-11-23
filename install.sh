#!/bin/bash
# Installs "Do A Hacking" into the Omarchy menu and binds it to SUPER + SHIFT + H.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
BIN="$BIN_DIR/do-a-hacking"
MENU="$HOME/.config/omarchy/extensions/omarchy-menu.jsonc"
BINDINGS="$HOME/.config/hypr/bindings.lua"
KEY="${HACKING_KEY:-SUPER + SHIFT + H}"
TAG="im-a-hacker-mommy"

# 1. launcher on PATH
mkdir -p "$BIN_DIR"
ln -sfn "$HERE/hack.py" "$BIN"
echo "  launcher   $BIN -> $HERE/hack.py"

# 2. menu entry (inserted before the closing brace of the JSONC file)
mkdir -p "$(dirname "$MENU")"
[[ -f "$MENU" ]] || printf '{\n}\n' > "$MENU"
python3 - "$MENU" "$BIN" "$TAG" <<'PY'
import re, sys
path, binpath, tag = sys.argv[1:4]
text = open(path, encoding="utf-8").read()
if tag in text:
    print("  menu       entry already present, skipping")
    sys.exit(0)
end = text.rstrip().rfind("}")
head, tail = text[:end], text[end:]
# last significant character before the brace, ignoring // comments and blank lines
body = "\n".join(l for l in head.splitlines() if not l.strip().startswith("//"))
last = body.rstrip()[-1:] if body.strip() else "{"
comma = "" if last in "{," else ","
# the tag goes on its own line: the menu validator rejects inline // comments
entry = (f'{comma}\n  // {tag}\n'
         f'  "doahacking": {{"icon": "", "label": "Do A Hacking", '
         f'"description": "I\'m a hacker, mommy!", '
         f'"action": "omarchy-launch-or-focus-tui {binpath}"}}\n')
open(path, "w", encoding="utf-8").write(head.rstrip("\n") + entry + tail)
print("  menu       added 'Do A Hacking' to the Omarchy menu")
PY

# 3. keybind
touch "$BINDINGS"
if grep -q ">>> $TAG >>>" "$BINDINGS"; then
  echo "  keybind    already present, skipping"
else
  cat >> "$BINDINGS" <<LUA

-- >>> $TAG >>>
o.bind("$KEY", "Do A Hacking", "omarchy-launch-or-focus-tui $BIN")
-- <<< $TAG <<<
LUA
  echo "  keybind    $KEY -> Do A Hacking"
fi

hyprctl reload >/dev/null 2>&1 || true
if hyprctl configerrors 2>/dev/null | grep -q .; then
  echo "  hyprland reported config errors:" >&2
  hyprctl configerrors >&2
  exit 1
fi
echo
echo "  installed. press $KEY, or find 'Do A Hacking' in the Omarchy menu."
echo "  tell her you're a hacker now."
