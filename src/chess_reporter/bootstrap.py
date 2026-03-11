#!/usr/bin/env python3
"""
Bootstrap
"""

from __future__ import annotations

from chess_reporter.database.database_bootstrapper import DatabaseBootstrapper
from chess_reporter.storage.storage_bootstrapper import StorageBootstrapper
from chess_reporter.utils.utils import setup_logger


def main():
    """
    Main function to bootstrap the Chess Reporter application.
    """
    StorageBootstrapper().bootstrap()
    DatabaseBootstrapper().bootstrap()


if __name__ == "__main__":
    setup_logger("DEBUG")
    main()
