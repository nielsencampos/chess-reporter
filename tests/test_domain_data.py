"""
Tests for domain/data: DataStatus.
"""

from __future__ import annotations

from chess_reporter.domain.data import DataStatus


def test_data_status_values() -> None:
    """
    All four status values exist with the correct string representations.
    """
    assert DataStatus.PENDING == "pending"
    assert DataStatus.IN_PROGRESS == "in_progress"
    assert DataStatus.COMPLETED == "completed"
    assert DataStatus.FAILED == "failed"


def test_data_status_priority_ordering() -> None:
    """
    Priority values follow the expected logical order.
    """
    assert DataStatus.PENDING.priority < DataStatus.IN_PROGRESS.priority
    assert DataStatus.IN_PROGRESS.priority < DataStatus.COMPLETED.priority
    assert DataStatus.COMPLETED.priority < DataStatus.FAILED.priority


def test_data_status_name_is_human_readable() -> None:
    """
    .name returns the human-readable display name, not the enum key.
    """
    assert DataStatus.PENDING.name == "Pending"
    assert DataStatus.IN_PROGRESS.name == "In progress"
    assert DataStatus.COMPLETED.name == "Completed"
    assert DataStatus.FAILED.name == "Failed"


def test_data_status_description_is_non_empty() -> None:
    """
    Every status has a non-empty description.
    """
    for status in DataStatus:
        assert len(status.description) > 0
