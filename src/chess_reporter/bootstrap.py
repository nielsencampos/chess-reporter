"""
Bootstrap
"""

from __future__ import annotations

from datetime import datetime, timezone
from sys import stdout

from loguru import logger

from chess_reporter.database.database_bootstrapper import DatabaseBootstrapper
from chess_reporter.storage.storage_bootstrapper import StorageBootstrapper


def setup_logger(level: str = "DEBUG") -> None:
    """
    Configures the logger for the application.

    Args:
        level (str): The logging level. Defaults to "DEBUG".
    """
    if level not in {"DEBUG", "INFO", "WARNING"}:
        raise ValueError(
            "Invalid logging level: {}. Valid levels are: DEBUG, INFO, WARNING.".format(level)
        )

    logger.remove()

    logger.add(
        stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    logger_file_name = "logs/chess_reporter_{}.log".format(timestamp)

    logger.add(
        logger_file_name,
        level=level,
        rotation="10 MB",  # novo arquivo a cada 10MB
        retention="7 days",  # mantém logs por 7 dias
        compression="zip",  # comprime logs antigos
    )


def main():
    """
    Main function to bootstrap the Chess Reporter application.
    """
    StorageBootstrapper().bootstrap()
    DatabaseBootstrapper().bootstrap()


if __name__ == "__main__":
    setup_logger("DEBUG")
    main()
