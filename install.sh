#!/bin/bash
# VibePrint3D — Install skill into Claude Code
set -e

SKILL_DIR="$HOME/.claude/skills/cadquery-3dprint"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing VibePrint3D skill..."

mkdir -p "$SKILL_DIR/scripts"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/scripts/preview.py" "$SKILL_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/viewer.py" "$SKILL_DIR/scripts/"

echo "Skill installed to $SKILL_DIR"

# Check for conda/cadquery
if command -v conda &>/dev/null; then
    if conda env list | grep -q cadquery; then
        echo "Conda 'cadquery' environment found."
    else
        echo ""
        echo "Conda found but no 'cadquery' environment. Create one with:"
        echo "  conda create -n cadquery python=3.11 cadquery trimesh matplotlib pillow numpy -c conda-forge -y"
    fi
else
    echo ""
    echo "Conda not found. Install miniforge first:"
    echo "  brew install --cask miniforge    # macOS"
    echo ""
    echo "Then create the cadquery environment:"
    echo "  conda create -n cadquery python=3.11 cadquery trimesh matplotlib pillow numpy -c conda-forge -y"
fi

echo ""
echo "Done. Restart Claude Code, then try:"
echo '  "Design me a 30mm test cube with 2mm walls and M3 holes in the corners"'
