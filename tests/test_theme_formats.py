"""
Tests to ensure theme output formats are correct.
"""

import json
from pathlib import Path

import pytest


# Path constants
PROJECT_ROOT = Path(__file__).parent.parent
ZED_THEME_PATH = PROJECT_ROOT / "zed" / "themes" / "looped.json"
CODE_DARK_THEME_PATH = PROJECT_ROOT / "code" / "looped-dark.json"
CODE_LIGHT_THEME_PATH = PROJECT_ROOT / "code" / "looped-light.json"


class TestZedThemeFormat:
    """Tests for Zed theme format validation."""

    @pytest.fixture
    def zed_theme(self):
        """Load the Zed theme JSON."""
        with open(ZED_THEME_PATH) as f:
            return json.load(f)

    def test_zed_theme_file_exists(self):
        """Verify Zed theme file exists."""
        assert ZED_THEME_PATH.exists(), f"Zed theme not found at {ZED_THEME_PATH}"

    def test_zed_root_structure(self, zed_theme):
        """Verify Zed theme has correct root structure."""
        assert "$schema" in zed_theme, "Missing $schema"
        assert zed_theme["$schema"] == "https://zed.dev/schema/themes/v0.2.0.json"
        assert "name" in zed_theme, "Missing name"
        assert "author" in zed_theme, "Missing author"
        assert "themes" in zed_theme, "Missing themes array"
        assert isinstance(zed_theme["themes"], list), "themes should be an array"
        assert len(zed_theme["themes"]) >= 2, (
            "Should have at least dark and light variants"
        )

    def test_zed_theme_variants(self, zed_theme):
        """Verify each theme variant has required properties."""
        for theme in zed_theme["themes"]:
            assert "name" in theme, "Theme variant missing name"
            assert "appearance" in theme, "Theme variant missing appearance"
            assert theme["appearance"] in ["dark", "light"], "Invalid appearance value"
            assert "style" in theme, "Theme variant missing style object"

    def test_zed_required_ui_properties(self, zed_theme):
        """Verify required UI properties are present."""
        required_props = [
            "background",
            "foreground",
            "border",  # Changed from border.color to match Zed format
            "border.focused",
            "text",  # Check base text property
            "text.muted",
            "icon",  # Check base icon property
            "icon.muted",
            "element.background",
            "element.hover",
            "editor.foreground",
            "editor.background",
            "editor.line_number",  # Verify it's flat, not editor.line_number.color
        ]

        for theme in zed_theme["themes"]:
            style = theme["style"]
            for prop in required_props:
                assert prop in style, (
                    f"Missing required property: {prop} in {theme['name']}"
                )

    def test_zed_syntax_structure(self, zed_theme):
        """Verify syntax highlighting structure is correct."""
        for theme in zed_theme["themes"]:
            style = theme["style"]
            assert "syntax" in style, f"Missing syntax section in {theme['name']}"

            syntax = style["syntax"]
            assert isinstance(syntax, dict), "syntax should be an object"

            # Check a few common syntax scopes exist
            common_scopes = ["comment", "keyword", "string", "function", "variable"]
            for scope in common_scopes:
                assert scope in syntax, f"Missing common syntax scope: {scope}"

    def test_zed_syntax_scope_format(self, zed_theme):
        """Verify each syntax scope has correct format."""
        for theme in zed_theme["themes"]:
            syntax = theme["style"]["syntax"]

            for scope_name, scope_props in syntax.items():
                # Check scope names don't have 'syntax.' prefix
                assert not scope_name.startswith("syntax."), (
                    f"Syntax scope should not have 'syntax.' prefix: {scope_name}"
                )

                # Check scope properties
                assert isinstance(scope_props, dict), (
                    f"Scope {scope_name} should be an object"
                )
                assert "color" in scope_props, f"Scope {scope_name} missing color"
                assert "font_style" in scope_props, (
                    f"Scope {scope_name} missing font_style"
                )
                assert "font_weight" in scope_props, (
                    f"Scope {scope_name} missing font_weight"
                )

                # Verify color format (hex color)
                color = scope_props["color"]
                assert color.startswith("#"), f"Color should be hex format: {color}"
                assert len(color) in [4, 7, 9], f"Invalid hex color length: {color}"

    def test_zed_no_vscode_properties(self, zed_theme):
        """Verify VS Code specific properties are not in Zed theme."""
        vscode_props = ["tokenColors", "colors", "semanticHighlighting", "type"]

        for theme in zed_theme["themes"]:
            for prop in vscode_props:
                assert prop not in theme, (
                    f"VS Code property '{prop}' found in Zed theme {theme['name']}"
                )

    def test_zed_color_format(self, zed_theme):
        """Verify all colors are in valid hex format."""

        def check_color(value, path=""):
            if isinstance(value, str) and value.startswith("#"):
                # Valid hex color formats: #RGB, #RRGGBB, #RRGGBBAA
                assert len(value) in [4, 7, 9], f"Invalid color at {path}: {value}"
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_color(v, f"{path}.{k}")

        for theme in zed_theme["themes"]:
            check_color(theme["style"], theme["name"])


class TestVSCodeThemeFormat:
    """Tests for VS Code theme format validation."""

    @pytest.fixture
    def vscode_dark_theme(self):
        """Load the VS Code dark theme JSON."""
        with open(CODE_DARK_THEME_PATH) as f:
            return json.load(f)

    @pytest.fixture
    def vscode_light_theme(self):
        """Load the VS Code light theme JSON."""
        with open(CODE_LIGHT_THEME_PATH) as f:
            return json.load(f)

    def test_vscode_theme_files_exist(self):
        """Verify VS Code theme files exist."""
        assert CODE_DARK_THEME_PATH.exists(), f"VS Code dark theme not found"
        assert CODE_LIGHT_THEME_PATH.exists(), f"VS Code light theme not found"

    def test_vscode_root_structure(self, vscode_dark_theme):
        """Verify VS Code theme has correct root structure."""
        assert "$schema" in vscode_dark_theme, "Missing $schema"
        assert vscode_dark_theme["$schema"] == "vscode://schemas/color-theme"
        assert "name" in vscode_dark_theme, "Missing name"
        assert "type" in vscode_dark_theme, "Missing type"
        assert vscode_dark_theme["type"] in ["dark", "light"], "Invalid type"
        assert "colors" in vscode_dark_theme, "Missing colors object"
        assert "tokenColors" in vscode_dark_theme, "Missing tokenColors array"

    def test_vscode_colors_structure(self, vscode_dark_theme):
        """Verify VS Code colors object structure."""
        colors = vscode_dark_theme["colors"]
        assert isinstance(colors, dict), "colors should be an object"

        # Check some common VS Code color keys
        # Note: These should NOT have 'editor.' prefix at root level in VS Code
        assert len(colors) > 0, "colors object should not be empty"

    def test_vscode_token_colors_structure(self, vscode_dark_theme):
        """Verify tokenColors array structure."""
        token_colors = vscode_dark_theme["tokenColors"]
        assert isinstance(token_colors, list), "tokenColors should be an array"
        assert len(token_colors) > 0, "tokenColors should not be empty"

        for token in token_colors:
            assert "settings" in token, "Token color missing settings"
            assert isinstance(token["settings"], dict), (
                "Token settings should be object"
            )

            # Either scope or scopes should be present (or just settings for global)
            if "scope" in token:
                assert isinstance(token["scope"], (str, list)), (
                    "scope should be string or array"
                )

    def test_vscode_no_zed_properties(self, vscode_dark_theme):
        """Verify Zed-specific properties are not in VS Code theme."""
        zed_props = ["appearance", "style.syntax", "style.border"]

        for prop in zed_props:
            parts = prop.split(".")
            current = vscode_dark_theme
            found = True
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break

            assert not found, f"Zed property '{prop}' found in VS Code theme"

    def test_vscode_color_format(self, vscode_dark_theme):
        """Verify VS Code colors are in valid format."""

        def check_value(value):
            if isinstance(value, str) and value.startswith("#"):
                # VS Code supports #RGB, #RRGGBB, #RRGGBBAA
                assert len(value) in [4, 7, 9], f"Invalid color: {value}"

        # Check colors object
        for color_value in vscode_dark_theme["colors"].values():
            check_value(color_value)

        # Check tokenColors
        for token in vscode_dark_theme["tokenColors"]:
            if "foreground" in token["settings"]:
                check_value(token["settings"]["foreground"])
            if "background" in token["settings"]:
                check_value(token["settings"]["background"])


class TestThemeConsistency:
    """Tests for consistency across theme formats."""

    @pytest.fixture
    def all_themes(self):
        """Load all theme files."""
        with open(ZED_THEME_PATH) as f:
            zed = json.load(f)
        with open(CODE_DARK_THEME_PATH) as f:
            vscode_dark = json.load(f)
        with open(CODE_LIGHT_THEME_PATH) as f:
            vscode_light = json.load(f)

        return {
            "zed": zed,
            "vscode_dark": vscode_dark,
            "vscode_light": vscode_light,
        }

    def test_theme_names_consistent(self, all_themes):
        """Verify theme names are consistent."""
        zed_dark = next(
            t for t in all_themes["zed"]["themes"] if t["appearance"] == "dark"
        )
        zed_light = next(
            t for t in all_themes["zed"]["themes"] if t["appearance"] == "light"
        )

        assert "Looped" in zed_dark["name"], "Zed dark theme should contain 'Looped'"
        assert "Looped" in zed_light["name"], "Zed light theme should contain 'Looped'"
        assert "Looped" in all_themes["vscode_dark"]["name"], (
            "VS Code dark theme should contain 'Looped'"
        )
        assert "Looped" in all_themes["vscode_light"]["name"], (
            "VS Code light theme should contain 'Looped'"
        )

    def test_primary_colors_defined(self, all_themes):
        """Verify primary colors are defined in all themes."""
        # Check Zed themes have key colors
        for theme in all_themes["zed"]["themes"]:
            style = theme["style"]
            assert "background" in style, f"Missing background in {theme['name']}"
            assert "foreground" in style, f"Missing foreground in {theme['name']}"

        # Check VS Code themes have colors
        for theme_key in ["vscode_dark", "vscode_light"]:
            theme = all_themes[theme_key]
            assert len(theme["colors"]) > 0, f"No colors defined in {theme['name']}"
            assert len(theme["tokenColors"]) > 0, f"No token colors in {theme['name']}"
