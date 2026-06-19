# Looped Editor Themes

[![Tests](https://github.com/loopedautomation/editor-themes/actions/workflows/test.yml/badge.svg)](https://github.com/loopedautomation/editor-themes/actions/workflows/test.yml)

Looped Automation's editor themes for VS Code, Zed, Warp, Oh My Posh, Herdr, and Ghostty are generated from a structured TOML template system. This repository contains the source templates, the build tooling, and the prebuilt themes.

## Prerequisites

- Python 3.13 or newer (the build script relies on the standard `tomllib` module)
- [uv](https://docs.astral.sh/uv/) for managing the virtual environment and running commands

## Getting Started

Clone the repository and install the dependencies into an isolated environment managed by uv:

```bash
git clone https://github.com/loopedautomation/editor-themes.git
cd editor-themes
uv sync
```

`uv sync` creates a dedicated virtual environment in `.venv/` and installs the dependencies declared in `pyproject.toml`.

## Building Themes

The build script compiles the TOML templates in `src/themes/` into VS Code color themes under `themes/`.

Run a one-off build:

```bash
uv run build.py        # Build VS Code themes
uv run build_zed.py    # Build Zed themes
```

Run the file watcher during active development (rebuilds all themes whenever template files change):

```bash
uv run watch.py
```

Keep the watcher running while you edit files in `src/templates/` or `src/themes/`. Generated JSON files appear in `code/` or `zed/themes/` and are ready for testing in your editor.

## Testing in VS Code

1. Open the repository folder in VS Code.
2. Start the extension host (`F5` or `Run and Debug > Start Debugging`).
3. In the Extension Development Host window, switch to the **Looped Dark** or **Looped Light** theme via the Command Palette.

The debugger automatically reloads whenever the generated theme JSON files change, so you can iterate quickly while the watcher is running.

## Project Structure

- `src/templates/` reusable color definitions and shared utilities
- `src/themes/` top-level theme descriptors that import templates and overrides
- `code/` generated VS Code themes consumed by the extension
- `zed/themes/` generated Zed themes
- `warp/` Warp terminal themes
- `oh-my-posh/` Oh My Posh prompt themes
- `herdr/` Herdr config snippets and installer
- `ghostty/` Ghostty terminal themes and installer
- `build.py` VS Code template compiler invoked by the watcher or directly
- `build_zed.py` Zed template compiler
- `build_herdr.py` Herdr config snippet compiler
- `build_ghostty.py` Ghostty theme compiler (reads the Warp presets)
- `watch.py` filesystem watcher that rebuilds all themes on change
- `package.json` VS Code extension manifest referencing generated themes
- `zed/extension.toml` Zed extension configuration

## Zed Themes

Looped themes are available for the [Zed editor](https://zed.dev/).

### Building Zed Themes

```bash
uv run build_zed.py
```

The generated themes will be in `zed/themes/`.

### Installing in Zed

For manual installation during development:

```bash
# macOS/Linux
mkdir -p ~/.config/zed/extensions
ln -s "$(pwd)/zed" ~/.config/zed/extensions/looped

# Windows (PowerShell, run as Administrator)
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Zed\extensions\looped" -Target "$(Get-Location)\zed"
```

Then restart Zed and select **Looped Dark** or **Looped Light** from the theme selector.

See [zed/README.md](zed/README.md) for detailed installation and usage instructions.

## Warp Themes

- The terminal presets sit under `warp/looped-dark.yaml` and `warp/looped-light.yaml`.
- Run `./warp/install.sh` to copy every YAML file in the folder into `~/.warp/themes/`.
- After installation, open Warp → Settings → Themes and pick **Looped Dark** or **Looped Light**.

## Oh My Posh Theme

- The prompt theme is in `oh-my-posh/looped-dark.omp.json`.
- Run `./oh-my-posh/install.sh` to copy it into Homebrew's themes folder and wire it into `.zshrc` (backs up your existing config first).
- If you prefer manual setup, add `eval "$(oh-my-posh init zsh --config $(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)"` to your shell init file.

## Herdr Theme

[Herdr](https://herdr.dev) is a terminal agent multiplexer. It has no installable theme
package — colors are set in `~/.config/herdr/config.toml` via a `[theme.custom]` override
block, so the Looped theme ships as a config snippet that maps the Looped palette onto
Herdr's supported fields (`panel_bg`, `accent`, `green`, `blue`, `red`, `yellow`).

### Building the Herdr Snippets

```bash
uv run build_herdr.py
```

This generates `herdr/looped-dark.toml` and `herdr/looped-light.toml`.

### Installing in Herdr

```bash
./herdr/install.sh           # install Looped Dark (default)
./herdr/install.sh --light   # install Looped Light
```

The installer writes the snippet to `~/.config/herdr/config.toml`, backing up any existing
config first. If you already have a `[theme]` section, it won't overwrite it — instead it
prints the snippet to merge manually.

For manual setup, copy the `[theme]` / `[theme.custom]` block from
`herdr/looped-dark.toml` (or `looped-light.toml`) into `~/.config/herdr/config.toml`, then
restart Herdr.

> Note: Herdr only themes its own UI chrome (panels, accent). The background of the
> terminal area inside panes is painted by your terminal emulator — see the Ghostty
> theme below to match the full window background.

## Ghostty Theme

[Ghostty](https://ghostty.org) themes set the full terminal window background and the 16
ANSI colors. The Looped Ghostty themes are generated from the Warp presets
(`warp/looped-*.yaml`), which are the source of truth for terminal colors, so Warp and
Ghostty stay in sync.

### Building the Ghostty Themes

```bash
uv run build_ghostty.py
```

This generates `ghostty/themes/looped-dark` and `ghostty/themes/looped-light`.

### Installing in Ghostty

```bash
./ghostty/install.sh           # use Looped Dark (default)
./ghostty/install.sh --light   # use Looped Light
```

The installer copies the theme files into `~/.config/ghostty/themes/` and sets
`theme = looped-dark` (or `looped-light`) in `~/.config/ghostty/config`, backing up any
existing config first. After installing, reload Ghostty's config (`Cmd+Shift+,`) or restart
Ghostty.

## License

This project is licensed under the [MIT](LICENSE) License.
