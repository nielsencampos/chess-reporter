"""
Chess domain: Position legal moves module
"""

from __future__ import annotations

from functools import cached_property

from pydantic import ConfigDict, RootModel

from chess_reporter.domain.move import MoveContext


class PositionLegalMoves(RootModel[list[MoveContext]]):
    """
    Position Legal Moves
    """

    model_config = ConfigDict(frozen=True)

    @property
    def count(self) -> int:
        """
        Count of legal moves available in the position
        """
        return len(self.root)

    @cached_property
    def captures(self) -> PositionLegalMoves:
        """
        Legal moves in the position that are captures
        """

        return PositionLegalMoves(
            [move_context for move_context in self.root if move_context.move_is_capture]
        )

    @property
    def captures_count(self) -> int:
        """
        Count of legal moves in the position that are captures
        """
        return self.captures.count
