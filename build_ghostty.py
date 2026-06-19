"""Generate Ghostty terminal themes from the Looped Warp color presets.

The Warp YAML presets (warp/looped-*.yaml) already encode the full 16-color ANSI
palette plus background/foreground/accent, and are the source of truth for terminal
colors. This script reformats them into Ghostty theme files so Warp and Ghostty stay
consistent. To avoid adding a YAML dependency, it uses a tiny parser tailored to the
fixed, simple structure of those preset files.
"""

from pathlib import Path

# ANSI palette index order for Ghostty's `palette = N=#hex` entries.
ANSI_ORDER = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def parse_warp_preset(path: Path):
    """Parse a Looped Warp YAML preset into a flat dict.

    Returns top-level scalars (accent, background, foreground, ...) plus
    'normal' and 'bright' sub-dicts of the terminal colors.
    """
    data = {"normal": {}, "bright": {}}
    section = None  # None | "normal" | "bright"

    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, value = raw.strip().partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if indent == 0:
            if key == "terminal_colors":
                section = None
            else:
                data[key] = value
        elif indent == 2:
            section = key  # "normal" or "bright"
        elif indent == 4 and section in ("normal", "bright"):
            data[section][key] = value

    return data


def build_ghostty_theme(warp_path: Path, output_dir: Path):
    preset = parse_warp_preset(warp_path)

    name = warp_path.stem  # e.g. "looped-dark"

    lines = [
        f"# {name} — generated from warp/{warp_path.name}. Do not edit by hand.",
        f"background = {preset['background']}",
        f"foreground = {preset['foreground']}",
    ]

    accent = preset.get("accent")
    if accent:
        lines.append(f"cursor-color = {accent}")
        lines.append(f"selection-background = {accent}")

    for i, color_name in enumerate(ANSI_ORDER):
        lines.append(f"palette = {i}={preset['normal'][color_name]}")
    for i, color_name in enumerate(ANSI_ORDER):
        lines.append(f"palette = {i + 8}={preset['bright'][color_name]}")

    content = "\n".join(lines) + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    # Ghostty theme files are extensionless.
    out_path = output_dir / name
    out_path.write_text(content)
    print(f"✅ Built {out_path}")


if __name__ == "__main__":
    warp_dir = Path("warp")
    output_dir = Path("ghostty") / "themes"

    presets = sorted(warp_dir.glob("looped-*.yaml"))
    if not presets:
        print(f"⚠️  No Warp presets found in {warp_dir}")
        exit(1)

    for preset in presets:
        try:
            build_ghostty_theme(preset, output_dir)
        except Exception as e:
            print(f"❌ Failed to build Ghostty theme from '{preset}': {e}")
