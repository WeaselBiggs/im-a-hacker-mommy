#!/bin/bash
# Removes the menu entry, keybind and launcher. Leaves the repo alone.
set -euo pipefail
TAG="im-a-hacker-mommy"
MENU="$HOME/.config/omarchy/extensions/omarchy-menu.jsonc"
BINDINGS="$HOME/.config/hypr/bindings.lua"

rm -f "$HOME/.local/bin/do-a-hacking"
[[ -f "$MENU" ]] && sed -i "/\/\/ $TAG\$/d" "$MENU"
[[ -f "$BINDINGS" ]] && sed -i "/^-- >>> $TAG >>>\$/,/^-- <<< $TAG <<<\$/d" "$BINDINGS"
hyprctl reload >/dev/null 2>&1 || true
echo "  uninstalled. you were never a hacker. the kettle is safe."
