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
    """Apply overrides to the base dictionary while retaining existing keys."""
    if not isinstance(overrides, dict):
        return base
    return deep_merge(base, overrides)


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
        raise KeyError(
            "The 'metadata.name' key is missing in the theme data. Please ensure it is defined in the theme file."
        )

    if not metadata_type:
        raise KeyError(
            "The 'metadata.type' key is missing in the theme data. Please ensure it is defined in the theme file."
        )

    # Process syntax tables to build token_colors with relative scope convention
    token_colors = []
    emitted = set()

    def resolve_color(val):
        # If already a hex color, return; else attempt palette lookup
        if isinstance(val, str) and re.match(r"^#([0-9a-fA-F]{3,8})$", val):
            return val
        if isinstance(val, str) and val in resolved.get("palette", {}):
            return resolved["palette"][val]
        return val

    def normalize_scopes(current_prefix, scopes):
        """Normalize scopes using strict leading-dot relative convention.
        Rules:
        - raw starting with '.' => relative fragment, prefix + '.' + fragment
        - raw without '.' and not equal to current prefix => simple fragment (relative)
        - any other (contains '.') => treated as absolute and left unchanged
        - raw equal to current prefix kept as is
        """
        normalized = []
        for raw in scopes:
            if not raw:
                continue
            if raw.startswith("."):
                frag = raw[1:]
                normalized.append(f"{current_prefix}.{frag}")
            elif "." not in raw and raw != current_prefix:
                normalized.append(f"{current_prefix}.{raw}")
            else:
                normalized.append(raw)
        seen = set()
        deduped = []
        for s in normalized:
            if s not in seen:
                seen.add(s)
                deduped.append(s)
        return deduped

    def process_syntax_table(table_name, table_data, prefix=""):
        current_prefix = f"{prefix}.{table_name}" if prefix else table_name
        is_group = bool(table_data.get("group"))
        # Only treat 'name' as a syntax property if it's a string (avoid collision with nested table named 'name')
        # Accept both 'scope' and 'scopes' (authoring convenience); normalize later
        name_prop = table_data.get("name")
        has_name_attr = isinstance(name_prop, str)
        has_syntax_properties = (
            any(k in table_data for k in ["color", "style", "scope", "scopes"])
            or has_name_attr
        ) and not is_group
        if has_syntax_properties:
            scope_key = None
            if "scope" in table_data:
                scope_key = "scope"
            elif "scopes" in table_data:  # alias
                scope_key = "scopes"
            if scope_key:
                scopes = table_data[scope_key]
                if isinstance(scopes, str):
                    scopes = [scopes]
                updated_scopes = normalize_scopes(current_prefix, scopes)
            else:
                updated_scopes = [current_prefix]

            # Split any comma-delimited scope strings that accidentally bundled multiple scopes
            split_scopes = []
            for s in updated_scopes:
                if isinstance(s, str) and "," in s:
                    parts = [p.strip() for p in s.split(",") if p.strip()]
                    if len(parts) > 1:
                        print(
                            f"⚠️  Splitting comma-delimited scope entry into multiple scopes: {s} -> {parts}"
                        )
                    split_scopes.extend(parts)
                else:
                    split_scopes.append(s)
            # Final sanitation: ensure all scopes are strings
            updated_scopes = [str(s) for s in split_scopes if s]

            token_color = {}
            if has_name_attr:
                token_color["name"] = name_prop
            elif "name" in table_data and not isinstance(name_prop, str):
                print(
                    f"⚠️  Ignoring non-string 'name' field at {current_prefix}; treat as nested scope container."
                )
            token_color["scope"] = updated_scopes
            settings = {}
            col = table_data.get("color")
            if col:
                settings["foreground"] = resolve_color(col)
            style_val = table_data.get("style")
            if style_val:
                settings["fontStyle"] = style_val
            token_color["settings"] = settings
            # Build a stable, hashable signature using JSON to avoid unhashable nested values
            try:
                sig = json.dumps(
                    {
                        "name": token_color.get("name"),
                        "scope": token_color.get("scope"),
                        "settings": token_color.get("settings"),
                    },
                    sort_keys=True,
                )
            except TypeError:
                # Fallback: coerce any problematic objects to string
                coerced = {
                    "name": token_color.get("name"),
                    "scope": [str(s) for s in token_color.get("scope", [])],
                    "settings": {
                        k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                        for k, v in token_color.get("settings", {}).items()
                    },
                }
                sig = json.dumps(coerced, sort_keys=True)
                token_color = coerced
            if sig not in emitted:
                emitted.add(sig)
                token_colors.append(token_color)
        for key, value in table_data.items():
            # Recurse into any dict child that is not one of the primitive style attributes
            if isinstance(value, dict) and key not in [
                "scope",
                "scopes",
                "color",
                "style",
                "group",
            ]:
                process_syntax_table(key, value, current_prefix)

    for key, value in resolved.items():
        if isinstance(value, dict) and key not in [
            "editor",
            "metadata",
            "palette",
            "import",
            "overrides",
        ]:
            process_syntax_table(key, value)

    def sort_key(token):
        name = token.get("name") or ""
        raw_scope = token.get("scope", [])
        # Guarantee list of strings for deterministic ordering
        if isinstance(raw_scope, (list, tuple)):
            safe_scope = [str(s) for s in raw_scope]
            try:
                scope_join = ",".join(sorted(safe_scope))
            except Exception:
                # Fallback: no internal sort if comparison fails (should not now)
                scope_join = ",".join(safe_scope)
        else:
            scope_join = str(raw_scope)
        settings_obj = token.get("settings", {})
        if not isinstance(settings_obj, dict):
            settings_obj = {"_value": settings_obj}
        settings_str = json.dumps(settings_obj, sort_keys=True)
        return (name, scope_join, settings_str)

    token_colors.sort(key=sort_key)

    # Flatten editor colors properly from nested editor dict
    editor_colors = {}
    if "editor" in resolved:
        flat_editor = flatten_dict(resolved["editor"], parent_key="editor")
        for k, v in flat_editor.items():
            if k.startswith("editor."):
                editor_colors[k.replace("editor.", "", 1)] = v

    # Use the extracted metadata values
    vscode_theme = {
        "$schema": "vscode://schemas/color-theme",
        "name": metadata_name,
        "type": metadata_type,
        "semanticHighlighting": resolved.get("metadata", {}).get(
            "semanticHighlighting", True
        ),
        "colors": editor_colors,
        "tokenColors": token_colors,
    }

    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / f"{metadata_name.lower().replace(' ', '-')}.json"
    with open(out_path, "w") as f:
        json.dump(vscode_theme, f, indent=2)

    print(f"✅ Built {out_path}")


if __name__ == "__main__":
    themes_dir = Path("src/themes")
    output_dir = Path("code")

    if not themes_dir.exists():
        print(f"⚠️  Themes directory not found: {themes_dir}")
        exit(1)

    theme_files = list(themes_dir.glob("*.toml"))
    if not theme_files:
        print(f"⚠️  No theme files found in {themes_dir}")
        exit(1)

    for theme_file in theme_files:
        try:
            build_theme(theme_file, output_dir)
        except Exception as e:
            print(f"❌ Failed to build theme '{theme_file}': {e}")
