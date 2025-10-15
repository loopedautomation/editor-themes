# Looped Editor Themes

Looped Automation's VS Code themes are generated from a structured TOML template system. This repository contains the source templates, the build tooling, and the prebuilt JSON themes that ship with the extension.

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
uv run build.py
```

Run the file watcher during active development (rebuilds whenever template files change):

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
- `build.py` template compiler invoked by the watcher or directly
- `watch.py` filesystem watcher that rebuilds themes on change
- `package.json` VS Code extension manifest referencing generated themes

# Warp Theme

- The Warp terminal theme lives in `themes/looped-*.json`.
- Copy or symlink the file into `~/.warp/themes/looped-*.json`, or use Warp's Settings → Themes → `Import from file` to pick it directly from this repository.
- Select **Looped Dark** inside Warp to apply the palette.

## Oh My Posh Theme

- The prompt theme is in `oh-my-posh/looped-dark.omp.json`.
- Run `./oh-my-posh/install.sh` to copy it into Homebrew's themes folder and wire it into `.zshrc` (backs up your existing config first).
- If you prefer manual setup, add `eval "$(oh-my-posh init zsh --config $(brew --prefix oh-my-posh)/themes/looped-dark.omp.json)"` to your shell init file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.