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


def flatten_dict(d, parent_key="", sep="."):
    """Flatten a nested dictionary into a single dictionary with dotted keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def apply_overrides(base, overrides):
    """Apply overrides to the base dictionary."""
    for key, value in overrides.items():
        base[key] = value  # Directly update the flattened key
    return base


def build_theme(theme_path: Path, output_dir: Path):
    theme = load_toml(theme_path)

    context = {}
    for name, imp_path in theme.get("import", {}).items():
        imp_data = load_toml(Path(theme_path.parent) / Path(imp_path))
        context = deep_merge(context, imp_data)

    # Merge theme-level definitions
    theme_data = deep_merge(context, theme)
    resolved = resolve_vars(theme_data, theme_data)

    # Apply overrides from the theme file after flattening
    if "overrides" in theme:
        resolved = apply_overrides(resolved, theme["overrides"])

    # Extract metadata before processing syntax
    metadata_name = resolved.get("metadata", {}).get("name")
    metadata_type = resolved.get("metadata", {}).get("type")

    if not metadata_name:
        raise KeyError("The 'metadata.name' key is missing in the theme data. Please ensure it is defined in the theme file.")

    if not metadata_type:
        raise KeyError("The 'metadata.type' key is missing in the theme data. Please ensure it is defined in the theme file.")

    # Process syntax tables to build token_colors
    token_colors = []
    
    def process_syntax_table(table_name, table_data, prefix=""):
        """Recursively process syntax tables and append table name to scope."""
        current_prefix = f"{prefix}.{table_name}" if prefix else table_name
        
        # Check if this table has color or style (it's a syntax definition)
        has_syntax_properties = "color" in table_data or "style" in table_data
        
        if has_syntax_properties:
            # If scope is defined, use it; otherwise use the table name as the scope
            if "scope" in table_data:
                scopes = table_data["scope"]
                if isinstance(scopes, str):
                    scopes = [scopes]
                # Append the table prefix to each scope
                updated_scopes = [f"{current_prefix}.{scope}" if scope else current_prefix for scope in scopes]
            else:
                # No scope defined, use the current_prefix as the scope
                updated_scopes = [current_prefix]
            
            # Build token_color with proper key order: name, scope, settings
            token_color = {}
            
            # Add name if present (first)
            if "name" in table_data:
                token_color["name"] = table_data["name"]
            
            # Add scope (second)
            token_color["scope"] = updated_scopes
            
            # Add settings (third)
            settings = {}
            if "color" in table_data and table_data["color"]:
                settings["foreground"] = table_data["color"]
            if "style" in table_data and table_data["style"]:
                settings["fontStyle"] = table_data["style"]
            
            token_color["settings"] = settings
            
            token_colors.append(token_color)
        
        # Recursively process nested tables
        for key, value in table_data.items():
            if isinstance(value, dict) and key not in ["scope", "name", "color", "style"]:
                process_syntax_table(key, value, current_prefix)
    
    # Process all top-level items looking for syntax definitions
    for key, value in resolved.items():
        if isinstance(value, dict) and key not in ["editor", "metadata", "palette", "import", "overrides"]:
            process_syntax_table(key, value)

    # Sort tokenColors by name, then scope, then settings
    def sort_key(token):
        name = token.get("name", "")
        scope = ",".join(sorted(token.get("scope", [])))
        settings = json.dumps(token.get("settings", {}), sort_keys=True)
        return (name, scope, settings)
    
    token_colors.sort(key=sort_key)

    # Use the extracted metadata values
    vscode_theme = {
        "$schema": "vscode://schemas/color-theme",
        "name": metadata_name,
        "type": metadata_type,
        "semanticHighlighting": resolved.get("metadata", {}).get("semanticHighlighting", True),
        "colors": {key.replace("editor.", "", 1): value for key, value in resolved.items() if key.startswith("editor.")},
        "tokenColors": token_colors,
    }

    output_dir.mkdir(exist_ok=True)
    out_path = (
        output_dir / f"{metadata_name.lower().replace(' ', '-')}.json"
    )
    with open(out_path, "w") as f:
        json.dump(vscode_theme, f, indent=2)

    print(f"✅ Built {out_path}")


if __name__ == "__main__":
    themes_dir = Path("src/themes")
    output_dir = Path("themes")
    for theme_file in themes_dir.glob("*.toml"):
        build_theme(theme_file, output_dir)
