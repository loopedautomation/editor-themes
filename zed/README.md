# Looped Themes for Zed

Looped Automation's themes for the [Zed editor](https://zed.dev/).

## Installation

### Option 1: Install from Zed Extensions (Coming Soon)

Once published to the Zed extensions registry, you'll be able to install directly from Zed:

1. Open Zed
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Linux/Windows)
3. Type "extensions"
4. Search for "Looped"
5. Click Install

### Option 2: Manual Installation (Development)

1. Clone this repository:
   ```bash
   git clone https://github.com/loopedautomation/editor-themes.git
   cd editor-themes
   ```

2. Build the themes:
   ```bash
   uv sync
   uv run build_zed.py
   ```

3. Open the Zed extensions page (Cmd + Shift + X) and click `Install Dev Extension`

4. Select the zed folder

## Usage

1. Open Zed's command palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Linux/Windows)
2. Type "theme"
3. Select "Theme Selector: Toggle"
4. Choose either:
   - **Looped Dark** - A dark theme with vibrant purple accents
   - **Looped Light** - A clean light theme with the same purple accent colors

## Available Themes

### Looped Dark
A modern dark theme featuring:
- Deep dark backgrounds (`#0A0B10`, `#14161B`)
- Vibrant purple primary color (`#685EF6`)
- Carefully selected syntax colors for optimal readability
- Subtle UI elements that don't distract from your code

### Looped Light
A crisp light theme featuring:
- Clean white backgrounds with subtle grays
- Same vibrant purple accents for consistency
- High contrast syntax colors optimized for light backgrounds
- Professional appearance for daytime coding

## Color Palette

Both themes use a consistent color palette:

| Color     | Dark Theme | Light Theme | Usage                    |
|-----------|------------|-------------|--------------------------|
| Primary   | `#685EF6`  | `#685EF6`   | Keywords, selections     |
| Secondary | `#8B8DFF`  | `#8B8DFF`   | Strings, constants       |
| Success   | `#389469`  | `#2D7A54`   | Git additions, success   |
| Error     | `#D02E1E`  | `#D02E1E`   | Errors, deletions        |
| Warning   | `#EE9A00`  | `#E68A00`   | Warnings, modifications  |
| Info      | `#8B8DFF`  | `#5B7FFF`   | Info, links              |

## Development

The Zed themes are generated from TOML templates in the `src/themes/zed/` directory.

To modify the themes:

1. Edit the TOML files in `src/themes/zed/` or `src/templates/zed/`
2. Run the build script:
   ```bash
   uv run build_zed.py
   ```
3. The generated themes will be in `zed/themes/`
4. Reload Zed to see your changes

For active development, use the watch script:
```bash
uv run watch.py
```

This will automatically rebuild both VS Code and Zed themes when you save changes.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## Feedback

Found a bug or have a suggestion? Please [open an issue](https://github.com/loopedautomation/editor-themes/issues) on GitHub.
