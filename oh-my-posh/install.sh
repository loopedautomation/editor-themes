#!/bin/bash

# Oh My Posh Looped Theme Installer
# This script installs the Looped Oh My Posh theme

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_FILE="$SCRIPT_DIR/looped-dark.omp.json"

echo -e "${BLUE}🎨 Installing Looped Oh My Posh Theme${NC}"
echo

# Check if Oh My Posh is installed
if ! command -v oh-my-posh &> /dev/null; then
    echo -e "${RED}❌ Oh My Posh is not installed${NC}"
    echo -e "${YELLOW}💡 Install it with: brew install jandedobbeleer/oh-my-posh/oh-my-posh${NC}"
    exit 1
fi

# Get Oh My Posh themes directory
THEMES_DIR="$(brew --prefix oh-my-posh)/themes"

if [ ! -d "$THEMES_DIR" ]; then
    echo -e "${RED}❌ Oh My Posh themes directory not found: $THEMES_DIR${NC}"
    exit 1
fi

# Copy theme file
echo -e "${BLUE}📂 Copying theme to Oh My Posh themes directory...${NC}"
cp "$THEME_FILE" "$THEMES_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Theme copied successfully to: $THEMES_DIR/looped-dark.omp.json${NC}"
else
    echo -e "${RED}❌ Failed to copy theme file${NC}"
    exit 1
fi

# Check if .zshrc exists
ZSHRC_FILE="$HOME/.zshrc"
BACKUP_FILE="$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"

echo
echo -e "${BLUE}🔧 Configuring shell...${NC}"

if [ -f "$ZSHRC_FILE" ]; then
    # Create backup
    echo -e "${YELLOW}💾 Creating backup: $BACKUP_FILE${NC}"
    cp "$ZSHRC_FILE" "$BACKUP_FILE"
    
    # Check if oh-my-posh is already configured
    if grep -q "oh-my-posh init" "$ZSHRC_FILE"; then
        echo -e "${YELLOW}⚠️  Oh My Posh is already configured in .zshrc${NC}"
        echo -e "${BLUE}💡 To use the Looped theme, update your oh-my-posh init line to:${NC}"
        echo -e "${GREEN}eval \"\$(oh-my-posh init zsh --config \$(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)\"${NC}"
    else
        # Add oh-my-posh initialization
        echo -e "${BLUE}📝 Adding Oh My Posh initialization to .zshrc...${NC}"
        echo "" >> "$ZSHRC_FILE"
        echo "# Oh My Posh - Looped Theme" >> "$ZSHRC_FILE"
        echo "eval \"\$(oh-my-posh init zsh --config \$(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)\"" >> "$ZSHRC_FILE"
        echo -e "${GREEN}✅ Added Oh My Posh configuration to .zshrc${NC}"
    fi
else
    # Create new .zshrc
    echo -e "${BLUE}📝 Creating new .zshrc file...${NC}"
    cat > "$ZSHRC_FILE" << EOF
# Oh My Posh - Looped Theme
eval "\$(oh-my-posh init zsh --config \$(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)"
EOF
    echo -e "${GREEN}✅ Created .zshrc with Oh My Posh configuration${NC}"
fi

echo
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "1. Restart your terminal or run: ${BLUE}source ~/.zshrc${NC}"
echo -e "2. Your prompt should now use the Looped Dark theme colors"
echo
echo -e "${BLUE}🔧 Manual configuration (if needed):${NC}"
echo -e "Add this line to your .zshrc:"
echo -e "${GREEN}eval \"\$(oh-my-posh init zsh --config \$(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)\"${NC}"
echo
echo -e "${YELLOW}💡 Tip: You can switch themes anytime by changing the --config parameter${NC}"