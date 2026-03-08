#!/usr/bin/env python3
"""
Clean up Python cache files and UV/pre-commit caches.
"""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree, which
from subprocess import run


def remove_path(path: Path) -> None:
    """
    Removes the specified path, whether it's a file or a directory.
    """
    if path.is_dir():
        rmtree(path)
        print(f"  ✓ Removed: {path}")
    elif path.is_file():
        path.unlink()
        print(f"  ✓ Removed: {path}")


def clean_pycache(root: Path) -> None:
    """
    Cleans up Python cache files by removing __pycache__ directories and .pyc files.
    """
    print("\n🐍 Cleaning Python cache...")

    for pycache in root.rglob("__pycache__"):
        remove_path(pycache)
    for pyc in root.rglob("*.pyc"):
        remove_path(pyc)


def clean_uv_cache() -> None:
    print("\n📦 Cleaning UV cache...")
    uv = which("uv")

    if uv is None:
        print("  ✗ uv not found in PATH.")
        return

    result = run(
        [uv, "cache", "clean"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  ✓ UV cache cleared.")
    else:
        print(f"  ✗ Error: {result.stderr.strip()}")


def clean_precommit_cache() -> None:
    """
    Cleans up pre-commit cache by running the 'pre-commit clean' command.
    """
    print("\n🔧 Cleaning pre-commit cache...")
    result = run(
        ["pre-commit", "clean"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  ✓ pre-commit cache cleared.")
    else:
        print(f"  ✗ Error: {result.stderr.strip()}")


def clean_logs(root: Path) -> None:
    """
    Cleans up log files by removing all .log files in the directory tree.
    """
    print("\n📄 Cleaning log files...")

    for log_file in root.rglob("*.log"):
        remove_path(log_file)


def main() -> None:
    """
    Main function to execute the cleanup process.
    """
    root = Path.cwd()
    print(f"🧹 Starting cleanup in: {root}")

    clean_pycache(root)
    clean_uv_cache()
    clean_precommit_cache()
    clean_logs(root)

    print("\n✅ Cleanup complete!\n")


if __name__ == "__main__":
    main()
