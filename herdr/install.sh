#!/bin/bash

# Herdr Looped Theme Installer
# Installs the Looped color overrides into ~/.config/herdr/config.toml.
#
# Usage:
#   ./herdr/install.sh           # install Looped Dark (default)
#   ./herdr/install.sh --light   # install Looped Light

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VARIANT="dark"
if [ "$1" == "--light" ]; then
    VARIANT="light"
fi

SNIPPET="$SCRIPT_DIR/looped-$VARIANT.toml"
CONFIG_DIR="$HOME/.config/herdr"
CONFIG_FILE="$CONFIG_DIR/config.toml"

if [ ! -f "$SNIPPET" ]; then
    echo "❌ Snippet not found: $SNIPPET"
    echo "💡 Run 'uv run build_herdr.py' first to generate it."
    exit 1
fi

echo "🎨 Installing Looped ${VARIANT} theme for Herdr"

mkdir -p "$CONFIG_DIR"

if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="$CONFIG_FILE.bak.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing config to: $BACKUP_FILE"
    cp "$CONFIG_FILE" "$BACKUP_FILE"

    if grep -q "^\[theme" "$CONFIG_FILE"; then
        echo "⚠️  An existing [theme] section was found in $CONFIG_FILE."
        echo "   To avoid clobbering other settings, the Looped block was NOT merged automatically."
        echo "   Replace your [theme] / [theme.custom] section with the contents of:"
        echo "     $SNIPPET"
        exit 0
    fi

    # No existing theme section: safe to append.
    echo "" >> "$CONFIG_FILE"
    cat "$SNIPPET" >> "$CONFIG_FILE"
    echo "✅ Appended Looped theme to $CONFIG_FILE"
else
    cp "$SNIPPET" "$CONFIG_FILE"
    echo "✅ Created $CONFIG_FILE with the Looped theme"
fi

echo
echo "🎉 Done. Restart Herdr (or reload its config) to apply the Looped colors."
