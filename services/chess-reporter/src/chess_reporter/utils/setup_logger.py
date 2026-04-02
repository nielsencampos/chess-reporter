"""
Utils package: Setup logger module
"""

from __future__ import annotations

from sys import stdout

from loguru import logger


def setup_logger(level: str = "DEBUG") -> None:
    """
    Configures the logger for the application.

    Args:
        level (str): The logging level. Defaults to "DEBUG".
    """
    if level not in {"DEBUG", "INFO", "WARNING"}:
        raise ValueError(f"Invalid logging level: {level}. Valid levels are: DEBUG, INFO, WARNING.")

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
