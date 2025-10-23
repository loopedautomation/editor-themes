# Looped Editor Themes

[![Tests](https://github.com/loopedautomation/editor-themes/actions/workflows/test.yml/badge.svg)](https://github.com/loopedautomation/editor-themes/actions/workflows/test.yml)

Looped Automation's editor themes for VS Code, Zed, Warp, and Oh My Posh are generated from a structured TOML template system. This repository contains the source templates, the build tooling, and the prebuilt themes.

## Prerequisites

- Git
- Python 3.13 or newer (the build script relies on the standard `tomllib` module)
- [uv](https://docs.astral.sh/uv/) for managing the virtual environment and running commands

You can install uv with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, ensure `uv` is on your `PATH` and restart your shell if needed.

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

Keep the watcher running while you edit files in `src/templates/` or `src/themes/`. Generated JSON files appear in `themes/` and are ready for testing in VS Code.

## Testing in VS Code

1. Open the repository folder in VS Code.
2. Start the extension host (`F5` or `Run and Debug > Start Debugging`).
3. In the Extension Development Host window, switch to the **Looped Dark** or **Looped Light** theme via the Command Palette.

The debugger automatically reloads whenever the generated theme JSON files change, so you can iterate quickly while the watcher is running.

## Project Structure

- `src/templates/` reusable color definitions and shared utilities
- `src/themes/` top-level theme descriptors that import templates and overrides
- `themes/` generated VS Code themes consumed by the extension
- `zed/` Zed editor extension and generated themes
- `warp/` Warp terminal themes
- `oh-my-posh/` Oh My Posh prompt themes
- `build.py` VS Code template compiler invoked by the watcher or directly
- `build_zed.py` Zed template compiler
- `watch.py` filesystem watcher that rebuilds all themes on change
- `package.json` VS Code extension manifest referencing generated themes

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.