"""
Utility functions for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha512
from json import dumps
from os import environ
from sys import stdout
from typing import Any, List

from loguru import logger


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

    logs_dir = environ.get("LOGS_PATH", "logs")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    logger_file_name = "{}/{}.log".format(logs_dir, timestamp)

    logger.add(
        logger_file_name,
        level=level,
        rotation="8 MB",
        retention="7 days",
        compression="zip",
    )


def generate_hash_id(values: List[Any]) -> str:
    """
    Generate a unique hash ID based on a list of values.

    Args:
        values (List[Any]): A list of values to generate the hash ID from.

    Returns:
        str: A unique hash ID generated from the input values.
    """
    concatenated_values: str = dumps(values, ensure_ascii=False, separators=(",", ":"), default=str)
    bytes_concatenated_values: bytes = concatenated_values.encode("utf-8")
    hash_value: str = sha512(bytes_concatenated_values).hexdigest()

    return hash_value
