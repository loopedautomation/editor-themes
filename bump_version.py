#!/usr/bin/env python3
"""Bump version across package.json and zed/extension.toml"""

import json
import re
import sys
from pathlib import Path


def bump_version(version: str, bump_type: str) -> str:
    """Bump semantic version number."""
    major, minor, patch = map(int, version.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Use major, minor, or patch.")


def update_package_json(new_version: str):
    """Update version in package.json"""
    package_path = Path("package.json")

    with open(package_path, "r") as f:
        package = json.load(f)

    old_version = package["version"]
    package["version"] = new_version

    with open(package_path, "w") as f:
        json.dump(package, f, indent=2)
        f.write("\n")  # Add trailing newline

    print(f"✅ Updated package.json: {old_version} → {new_version}")
    return old_version


def update_extension_toml(new_version: str):
    """Update version in zed/extension.toml"""
    extension_path = Path("zed/extension.toml")

    with open(extension_path, "r") as f:
        content = f.read()

    # Find current version
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in extension.toml")

    old_version = match.group(1)

    # Replace version
    new_content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)

    with open(extension_path, "w") as f:
        f.write(new_content)

    print(f"✅ Updated zed/extension.toml: {old_version} → {new_version}")


def update_pyproject_toml(new_version: str):
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")

    with open(pyproject_path, "r") as f:
        content = f.read()

    # Find current version
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    old_version = match.group(1)

    # Replace version
    new_content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)

    with open(pyproject_path, "w") as f:
        f.write(new_content)

    print(f"✅ Updated pyproject.toml: {old_version} → {new_version}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <major|minor|patch>")
        sys.exit(1)

    bump_type = sys.argv[1].lower()

    if bump_type not in ["major", "minor", "patch"]:
        print("Error: bump type must be 'major', 'minor', or 'patch'")
        sys.exit(1)

    # Read current version from package.json
    with open("package.json", "r") as f:
        package = json.load(f)

    current_version = package["version"]
    new_version = bump_version(current_version, bump_type)

    print(f"\n🔄 Bumping version: {current_version} → {new_version} ({bump_type})\n")

    # Update both files
    update_package_json(new_version)
    update_extension_toml(new_version)
    update_pyproject_toml(new_version)

    print(f"\n✨ Version bump complete! New version: {new_version}")
    print("\nNext steps:")
    print("  git add package.json zed/extension.toml")
    print(f"  git commit -m 'Bump version to {new_version}'")
    print(f"  git tag v{new_version}")
    print("  git push && git push --tags")


if __name__ == "__main__":
    main()
