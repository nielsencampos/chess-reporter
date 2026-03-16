"""
Chess domain: Move comment title module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class MoveCommentTitle(StrEnum):
    """
    Move Comment Title

    Values:
        CLOCK_TIME (str): Clock time resting information
        ELAPSED_MOVE_TIME (str): Elapsed move time information
        ECO (str): ECO code information
        OPENING (str): Opening information
        GAME_PHASE (str): Game phase information
        EVALUATION (str): Evaluation information
        ACCURACY (str): Move accuracy information
        CLASSIFICATION (str): Move classification information
    """

    CLOCK_TIME = "clk"
    ELAPSED_MOVE_TIME = "emt"
    ECO = "eco"
    OPENING = "open"
    GAME_PHASE = "phase"
    EVALUATION = "eval"
    ACCURACY = "acc"
    CLASSIFICATION = "class"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)


PRIORITIES: Final[MappingProxyType[MoveCommentTitle, int]] = MappingProxyType(
    {
        MoveCommentTitle.CLOCK_TIME: 1,
        MoveCommentTitle.ELAPSED_MOVE_TIME: 2,
        MoveCommentTitle.ECO: 3,
        MoveCommentTitle.OPENING: 4,
        MoveCommentTitle.GAME_PHASE: 5,
        MoveCommentTitle.EVALUATION: 6,
        MoveCommentTitle.ACCURACY: 7,
        MoveCommentTitle.CLASSIFICATION: 8,
    }
)
