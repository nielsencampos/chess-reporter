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
    precommit = which("pre-commit")

    if precommit is None:
        print("  ✗ pre-commit not found in PATH.")
        return
    result = run(
        [precommit, "clean"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  ✓ pre-commit cache cleared.")
    else:
        print(f"  ✗ Error: {result.stderr.strip()}")


def clean_logs(root: Path) -> None:
    """
    Cleans up log files by removing all .log and compressed .zip log files.
    """
    print("\n📄 Cleaning log files...")

    for log_file in root.rglob("*.log"):
        remove_path(log_file)
    for zip_file in root.rglob("*.zip"):
        remove_path(zip_file)


def clean_tool_caches(root: Path) -> None:
    """
    Cleans up tool cache directories: .pytest_cache, .ruff_cache.
    """
    print("\n🗑️  Cleaning tool caches...")

    for name in (".pytest_cache", ".ruff_cache"):
        for path in root.rglob(name):
            remove_path(path)


def clean_jupyter(root: Path) -> None:
    """
    Cleans up Jupyter checkpoint directories.
    """
    print("\n📓 Cleaning Jupyter checkpoints...")

    for path in root.rglob(".ipynb_checkpoints"):
        remove_path(path)


def clean_duckdb_wal(root: Path) -> None:
    """
    Cleans up leftover DuckDB WAL files.
    """
    print("\n🦆 Cleaning DuckDB WAL files...")

    for wal_file in root.rglob("*.duckdb.wal"):
        remove_path(wal_file)


def main() -> None:
    """
    Main function to execute the cleanup process.
    """
    root = Path.cwd()
    print(f"🧹 Starting cleanup in: {root}")

    clean_pycache(root)
    clean_tool_caches(root)
    clean_uv_cache()
    clean_precommit_cache()
    clean_logs(root)
    clean_jupyter(root)
    clean_duckdb_wal(root)

    print("\n✅ Cleanup complete!\n")


if __name__ == "__main__":
    main()
