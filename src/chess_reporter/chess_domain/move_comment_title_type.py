"""
Chess domain: Move comment title type
"""

from __future__ import annotations

from enum import StrEnum


class MoveCommentTitleType(StrEnum):
    """
    Enumeration for the title of a comment associated with a chess move.

    Values:
        ACCURACY (str): Move accuracy information
        CLASSIFICATION (str): Move classification information
        CLOCK_TIME (str): Clock time resting information
        ECO (str): ECO code information
        ELAPSED_MOVE_TIME (str): Elapsed move time information
        EVALUATION (str): Evaluation information
        GAME_PHASE (str): Game phase information
        OPENING (str): Opening information
    """

    ACCURACY = "acc"
    CLASSIFICATION = "class"
    CLOCK_TIME = "clk"
    ECO = "eco"
    ELAPSED_MOVE_TIME = "emt"
    EVALUATION = "eval"
    GAME_PHASE = "phase"
    OPENING = "open"
