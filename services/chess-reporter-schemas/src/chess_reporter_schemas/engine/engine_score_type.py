"""
Schemas: Engine score type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class EngineScoreType(StrEnum):
    """
    Engine Score Type

    Values:
        CP: Centipawns score
        MATE: Mate score
    """

    CP = "cp"
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

    @property
    def description(self) -> str:
        """
        Description
        """
        return DESCRIPTIONS.get(self, "Unknown score type")


PRIORITIES: Final[MappingProxyType[EngineScoreType, int]] = MappingProxyType(
    {
        EngineScoreType.CP: 1,
        EngineScoreType.MATE: 2,
    }
)
CHARACTERS: Final[MappingProxyType[EngineScoreType, str]] = MappingProxyType(
    {
        EngineScoreType.CP: "C",
        EngineScoreType.MATE: "M",
    }
)
DESCRIPTIONS: Final[MappingProxyType[EngineScoreType, str]] = MappingProxyType(
    {
        EngineScoreType.CP: "Centipawns score",
        EngineScoreType.MATE: "Mate score",
    }
)
