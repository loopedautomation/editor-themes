import tomllib
import json
from pathlib import Path


def load_toml(path: Path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def deep_merge(a, b):
    """Deep merge two dictionaries."""
    for key, val in b.items():
        if isinstance(val, dict) and key in a:
            a[key] = deep_merge(a[key], val)
        else:
            a[key] = val
    return a


def resolve_vars(obj, context):
    """Resolve ${variable.path} references in strings."""
    if isinstance(obj, dict):
        return {k: resolve_vars(v, context) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_vars(v, context) for v in obj]
    if isinstance(obj, str):
        import re

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


def flatten_dict(d, parent_key="", sep="."):
    """Flatten a nested dictionary into dotted keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def build_zed_theme_item(theme_path: Path):
    """Build and return a single Zed theme item (for inclusion in a combined file)."""
    theme = load_toml(theme_path)

    # Load imports - only process imports that start with "zed_"
    context = {}
    for name, imp_path in theme.get("import", {}).items():
        if name.startswith("zed_"):
            imp_data = load_toml(Path(theme_path.parent) / Path(imp_path))
            # Just merge the imported data directly into context
            # The imported files already have the correct structure (e.g., {editor: {...}, syntax: {...}})
            context = deep_merge(context, imp_data)

    # Merge theme data
    theme_data = deep_merge(context, theme)
    resolved = resolve_vars(theme_data, theme_data)

    # Extract metadata
    metadata = resolved.get("metadata", {})
    theme_name = metadata.get("name")
    theme_type = metadata.get("type", "dark")

    if not theme_name:
        raise KeyError("The 'metadata.name' key is missing in the theme data.")

    # Map theme type to Zed appearance
    appearance = "dark" if theme_type == "dark" else "light"

    # Build style object
    style = {}

    # First, handle [root] table - these properties go directly to root level
    if "root" in resolved:
        for key, value in resolved["root"].items():
            zed_key = key.replace("-", "_")
            style[zed_key] = value

    # Then, add other top-level properties
    top_level_excludes = {"metadata", "palette", "import", "editor", "syntax", "root"}
    for key, value in resolved.items():
        if key not in top_level_excludes and not isinstance(value, dict):
            # Top-level scalar properties go directly into style
            zed_key = key.replace("-", "_")
            style[zed_key] = value
        elif key not in top_level_excludes and isinstance(value, dict):
            # Top-level dict properties (like [border], [text], [icon]) get flattened
            flat_top = flatten_dict({key: value})
            for nested_key, nested_value in flat_top.items():
                zed_key = nested_key.replace("-", "_")
                style[zed_key] = nested_value

    # Then, flatten editor colors (these can override top-level if needed)
    if "editor" in resolved:
        flat_editor = flatten_dict(resolved["editor"])
        for key, value in flat_editor.items():
            # Convert to Zed format (use snake_case)
            # Preserve the editor. prefix
            zed_key = f"editor.{key}".replace("-", "_")
            style[zed_key] = value

    # Add syntax colors
    if "syntax" in resolved:
        style["syntax"] = {}

        # Flatten the syntax section to handle nested tables like [syntax.comment.doc]
        flat_syntax = flatten_dict(resolved["syntax"])

        # Group properties by scope name
        syntax_scopes = {}
        for key, value in flat_syntax.items():
            parts = key.split(".")
            if len(parts) == 1:
                # Single property like "color" - skip root-level syntax properties
                continue
            else:
                # Nested like "comment.color" or "comment.doc.color"
                # The scope is everything except the last part (which is the property)
                scope_name = ".".join(parts[:-1])
                prop_name = parts[-1]

            if scope_name not in syntax_scopes:
                syntax_scopes[scope_name] = {}
            syntax_scopes[scope_name][prop_name] = value

        # Convert to Zed format
        for scope_name, props in syntax_scopes.items():
            scope_style = {}

            if "color" in props:
                scope_style["color"] = props["color"]

            if "font_style" in props:
                scope_style["font_style"] = props["font_style"]
            else:
                scope_style["font_style"] = None

            if "font_weight" in props:
                scope_style["font_weight"] = props["font_weight"]
            else:
                scope_style["font_weight"] = None

            style["syntax"][scope_name] = scope_style

    # Return the inner theme entry (to be combined into a single file)
    theme_item = {"name": theme_name, "appearance": appearance, "style": style}
    return theme_item


if __name__ == "__main__":
    # Read single-file-per-theme TOML files from the top-level src/themes folder
    themes_dir = Path("src/themes")
    output_file = Path("zed/themes/looped.json")

    # Ensure the source directory exists
    if not themes_dir.exists():
        print(f"⚠️  Themes directory not found: {themes_dir}")
        print("Creating directory...")
        themes_dir.mkdir(parents=True, exist_ok=True)

    # Collect only top-level TOML files from src/themes (one file per theme)
    theme_files = sorted([p for p in themes_dir.glob("*.toml") if p.is_file()])
    if not theme_files:
        print(f"⚠️  No theme files found in {themes_dir}")
    else:
        theme_items = []
        for theme_file in theme_files:
            try:
                item = build_zed_theme_item(theme_file)
                theme_items.append(item)
                print(f"✅ Prepared theme item: {item.get('name')}")
            except Exception as e:
                print(f"❌ Failed to build theme '{theme_file}': {e}")

        # Build combined object to emit a single JSON file which contains an array of themes
        combined = {
            "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
            "name": "Looped",
            "author": "Looped Automation",
            "themes": theme_items,
        }

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write single combined file
        with open(output_file, "w") as f:
            json.dump(combined, f, indent=2)

        print(f"✅ Built combined Zed themes file: {output_file}")
