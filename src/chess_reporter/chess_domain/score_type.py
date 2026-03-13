"""
Chess domain: Score type
"""

from __future__ import annotations

from enum import StrEnum


class ScoreType(StrEnum):
    """
    Enumeration of score types for chess engine evaluations.

    Values:
        CP: Centipawns score.
        MATE: Mate score.
    """

    CP = "cp"
    MATE = "mate"
