import tomllib
import json
import re
from pathlib import Path

def load_toml(path: Path):
    with open(path, "rb") as f:
        return tomllib.load(f)

def deep_merge(a, b):
    for key, val in b.items():
        if isinstance(val, dict) and key in a:
            a[key] = deep_merge(a[key], val)
        else:
            a[key] = val
    return a

def resolve_vars(obj, context):
    if isinstance(obj, dict):
        return {k: resolve_vars(v, context) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_vars(v, context) for v in obj]
    if isinstance(obj, str):
        def repl(m):
            path = m.group(1).split(".")
            val = context
            for p in path:
                val = val.get(p, None)
                if val is None:
                    return m.group(0)
            return val
        return re.sub(r"\$\{([a-zA-Z0-9_.]+)\}", repl, obj)
    return obj

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten a nested dictionary into a single dictionary with dotted keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def build_theme(theme_path: Path, output_dir: Path):
    theme = load_toml(theme_path)

    context = {}
    for name, imp_path in theme.get("import", {}).items():
        imp_data = load_toml(Path(theme_path.parent) / Path(imp_path))
        context = deep_merge(context, imp_data)

    # Merge theme-level definitions
    theme_data = deep_merge(context, theme)
    resolved = resolve_vars(theme_data, theme_data)

    # Flatten all top-level sections
    for section in resolved:
        if isinstance(resolved[section], dict):
            resolved[section] = flatten_dict(resolved[section])

    # Ensure syntax section is a list before processing
    if "syntax" in resolved and isinstance(resolved["syntax"], dict):
        resolved["syntax"] = list(flatten_dict(resolved["syntax"].items()))

    # Assemble VSCode JSON format
    vscode_theme = {
        "$schema": "vscode://schemas/color-theme",
        "name": resolved["metadata"]["name"],
        "type": resolved["metadata"]["type"],
        "semanticHighlighting": resolved["metadata"].get("semanticHighlighting", True),
        "colors": resolved.get("editor", {}),
        "tokenColors": resolved.get("syntax", []),
    }

    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / f"{resolved['metadata']['name'].lower().replace(' ', '-')}.json"
    with open(out_path, "w") as f:
        json.dump(vscode_theme, f, indent=2)

    print(f"✅ Built {out_path}")

if __name__ == "__main__":
    themes_dir = Path("src/themes")
    output_dir = Path("themes")
    for theme_file in themes_dir.glob("*.toml"):
        build_theme(theme_file, output_dir)