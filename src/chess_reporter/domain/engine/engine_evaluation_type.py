"""
Chess domain: Engine evaluation type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class EngineEvaluationType(StrEnum):
    """
    Engine Evaluation Type

    Values:
        NORMAL (str): Regular engine evaluation
        FAILED (str): Engine evaluation failed due to an error
        FORCED (str): Terminal position (checkmate, stalemate, etc.)
    """

    NORMAL = "normal"
    FAILED = "failed"
    FORCED = "forced"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)

    @property
    def character(self) -> str:
        """
        Character
        """

        return CHARACTERS.get(self, "∅")

    @property
    def engine_used(self) -> bool:
        """
        Engine used
        """
        return self is not EngineEvaluationType.FORCED


PRIORITIES: Final[MappingProxyType[EngineEvaluationType, int]] = MappingProxyType(
    {
        EngineEvaluationType.NORMAL: 1,
        EngineEvaluationType.FAILED: 2,
        EngineEvaluationType.FORCED: 3,
    }
)

CHARACTERS: Final[MappingProxyType[EngineEvaluationType, str]] = MappingProxyType(
    {
        EngineEvaluationType.NORMAL: "N",
        EngineEvaluationType.FAILED: "X",
        EngineEvaluationType.FORCED: "F",
    }
)
