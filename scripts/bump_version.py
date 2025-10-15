#!/usr/bin/env python3
"""Bump project version in pyproject.toml and package.json, then run `uv sync`.

Usage:
    python scripts/bump_version.py 1.2.3

The provided version string replaces:
    - `version` in pyproject.toml
    - `version` in package.json

After updating files the script executes `uv sync` to refresh the local environment.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
PACKAGE_JSON_PATH = REPO_ROOT / "package.json"


def update_pyproject(version: str) -> None:
    text = PYPROJECT_PATH.read_text()
    lines = text.splitlines()

    in_project = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = stripped == "[project]"
        elif in_project and stripped.startswith("version"):
            lines[idx] = f'version = "{version}"'
            PYPROJECT_PATH.write_text("\n".join(lines) + "\n")
            return

    # If the version field is missing, insert it after the `[project]` header
    for idx, line in enumerate(lines):
        if line.strip() == "[project]":
            insert_at = idx + 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            lines.insert(insert_at, f'version = "{version}"')
            PYPROJECT_PATH.write_text("\n".join(lines) + "\n")
            return

    raise ValueError("Could not locate [project] table in pyproject.toml")


def update_package_json(version: str) -> None:
    data = json.loads(PACKAGE_JSON_PATH.read_text())
    data["version"] = version
    PACKAGE_JSON_PATH.write_text(json.dumps(data, indent=2) + "\n")


def run_uv_sync() -> None:
    try:
        subprocess.run(["uv", "sync"], check=True)
    except FileNotFoundError as exc:  # uv not installed
        raise FileNotFoundError(
            "uv command not found. Install uv before running this script."
        ) from exc


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="New semantic version, e.g. 1.2.3")
    args = parser.parse_args(argv)

    version = args.version
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        parser.error("version must match MAJOR.MINOR.PATCH (e.g. 1.2.3)")

    update_pyproject(version)
    update_package_json(version)
    run_uv_sync()
    print(f"Updated project version to {version} and ran 'uv sync'.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
