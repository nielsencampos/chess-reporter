#!/usr/bin/env python3
"""
Bootstrap
"""

from __future__ import annotations

from chess_reporter.utils.setup_logger import setup_logger


def main() -> None:
    """
    Entry point for the chess-reporter service.
    """
    setup_logger("INFO")


if __name__ == "__main__":
    main()
