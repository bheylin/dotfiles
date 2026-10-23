#!/bin/sh
# Area screenshot: drag to select a region, save a timestamped PNG and copy it
# to the clipboard. If the selection is cancelled, maim exits non-zero and the
# && short-circuits, so nothing is saved or copied.
set -eu

dir="$HOME/Pictures/Screenshots"
mkdir -p "$dir"
file="$dir/$(date +%Y-%m-%d_%H-%M-%S).png"

maim --select "$file" && xclip -selection clipboard -t image/png "$file"
