import tomllib
from pathlib import Path


def load_toml(path: Path):
    with open(path, "rb") as f:
        return tomllib.load(f)


# Map Herdr's limited [theme.custom] override fields onto Looped palette keys.
# Herdr only supports these six custom fields (see https://herdr.dev/docs/configuration/).
HERDR_FIELD_MAP = {
    "panel_bg": "base_100",
    "accent": "primary",
    "green": "success",
    "blue": "info",
    "red": "error",
    "yellow": "warning",
}

# Built-in Herdr base theme each variant builds on. The base supplies colors for all the
# UI surfaces our six [theme.custom] fields don't cover; our overrides are layered on top.
# A full base (one-dark/one-light) gives a fully themed look, unlike "terminal" which
# defers most surfaces to the user's terminal palette.
BASE_THEME = {
    "dark": "one-dark",
    "light": "one-light",
}


def build_herdr_theme(theme_path: Path, output_dir: Path):
    theme = load_toml(theme_path)
    palette = theme.get("palette", {})
    metadata = theme.get("metadata", {})

    name = metadata.get("name")
    theme_type = metadata.get("type", "dark")

    if not name:
        raise KeyError("The 'metadata.name' key is missing in the theme data.")

    custom = {}
    for herdr_field, palette_key in HERDR_FIELD_MAP.items():
        value = palette.get(palette_key)
        if value is None:
            raise KeyError(
                f"Palette key '{palette_key}' (for Herdr field '{herdr_field}') "
                f"missing in {theme_path}"
            )
        custom[herdr_field] = value

    base = BASE_THEME.get(theme_type, "terminal")

    # Emit a hand-formatted TOML snippet (aligned for readability). This is a config
    # fragment a user merges into ~/.config/herdr/config.toml.
    width = max(len(k) for k in custom)
    lines = [
        f"# {name} — generated from {theme_path.name}. Do not edit by hand.",
        "# Merge this into ~/.config/herdr/config.toml.",
        "[theme]",
        f'name = "{base}"',
        "",
        "[theme.custom]",
    ]
    for field, value in custom.items():
        lines.append(f'{field.ljust(width)} = "{value}"')
    content = "\n".join(lines) + "\n"

    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / f"{name.lower().replace(' ', '-')}.toml"
    with open(out_path, "w") as f:
        f.write(content)

    print(f"✅ Built {out_path}")


if __name__ == "__main__":
    themes_dir = Path("src/themes")
    output_dir = Path("herdr")

    if not themes_dir.exists():
        print(f"⚠️  Themes directory not found: {themes_dir}")
        exit(1)

    theme_files = list(themes_dir.glob("*.toml"))
    if not theme_files:
        print(f"⚠️  No theme files found in {themes_dir}")
        exit(1)

    for theme_file in theme_files:
        try:
            build_herdr_theme(theme_file, output_dir)
        except Exception as e:
            print(f"❌ Failed to build theme '{theme_file}': {e}")
