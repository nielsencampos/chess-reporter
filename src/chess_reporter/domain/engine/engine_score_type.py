"""
Chess domain: Engine score type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class EngineScoreType(StrEnum):
    """
    Engine Score Type

    Values:
        CENTIPAWNS: Centipawns score
        MATE: Mate score
    """

    CENTIPAWNS = "centipawns"
    MATE = "mate"

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


PRIORITIES: Final[MappingProxyType[EngineScoreType, int]] = MappingProxyType(
    {
        EngineScoreType.CENTIPAWNS: 1,
        EngineScoreType.MATE: 2,
    }
)

CHARACTERS: Final[MappingProxyType[EngineScoreType, str]] = MappingProxyType(
    {
        EngineScoreType.CENTIPAWNS: "C",
        EngineScoreType.MATE: "M",
    }
)
