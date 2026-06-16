#!/bin/bash

# Ghostty Looped Theme Installer
# Copies the Looped theme files into Ghostty's themes dir and sets the active theme.
#
# Usage:
#   ./ghostty/install.sh           # use Looped Dark (default)
#   ./ghostty/install.sh --light   # use Looped Light

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VARIANT="dark"
if [ "$1" == "--light" ]; then
    VARIANT="light"
fi
THEME_NAME="looped-$VARIANT"

CONFIG_DIR="$HOME/.config/ghostty"
THEMES_DIR="$CONFIG_DIR/themes"
CONFIG_FILE="$CONFIG_DIR/config"

if [ ! -d "$SCRIPT_DIR/themes" ]; then
    echo "❌ Theme files not found. Run 'uv run build_ghostty.py' first."
    exit 1
fi

echo "🎨 Installing Looped ${VARIANT} theme for Ghostty"

mkdir -p "$THEMES_DIR"
cp "$SCRIPT_DIR/themes/"looped-* "$THEMES_DIR/"
echo "✅ Copied theme files to $THEMES_DIR"

if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="$CONFIG_FILE.bak.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing config to: $BACKUP_FILE"
    cp "$CONFIG_FILE" "$BACKUP_FILE"

    if grep -q "^theme[[:space:]]*=" "$CONFIG_FILE"; then
        # Replace existing theme line in place.
        sed -i '' "s/^theme[[:space:]]*=.*/theme = $THEME_NAME/" "$CONFIG_FILE"
        echo "✅ Updated theme line in $CONFIG_FILE"
    else
        printf '\ntheme = %s\n' "$THEME_NAME" >> "$CONFIG_FILE"
        echo "✅ Appended theme to $CONFIG_FILE"
    fi
else
    printf 'theme = %s\n' "$THEME_NAME" > "$CONFIG_FILE"
    echo "✅ Created $CONFIG_FILE with theme = $THEME_NAME"
fi

echo
echo "🎉 Done. Reload Ghostty config (Cmd+Shift+,) or restart Ghostty to apply."
