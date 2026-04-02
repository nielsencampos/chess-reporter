"""
Evaluation package: parameters module
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationParameters:
    """
    Evaluation Parameters

    Attributes:
        pawn_value: Material value of a pawn in centipawns (default: 1.0).
        knight_value: Material value of a knight in centipawns (default: 3.0).
        bishop_value: Material value of a bishop in centipawns (default: 3.0).
        rook_value: Material value of a rook in centipawns (default: 5.0).
        queen_value: Material value of a queen in centipawns (default: 9.0).
        winning_threshold: Score threshold to classify a position as winning
            in centipawns (default: 3.0).
        equal_threshold: Score threshold to classify a position as equal
            in centipawns (default: 0.5).
        mate_value: Centipawn score representing mate in N moves
            (default: 1000.0).
        table_name: Database table identifier for persistence
            (default: "chess_reporter.evaluation_parameter").
    """

    # Material scale
    pawn_value: float = field(default=1.0, init=False)
    knight_value: float = field(default=3.0, init=False)
    bishop_value: float = field(default=3.0, init=False)
    rook_value: float = field(default=5.0, init=False)
    queen_value: float = field(default=9.0, init=False)

    # Thresholds for categorizing evaluation scores (in centipawns)
    winning_threshold: float = field(default=3.0, init=False)
    equal_threshold: float = field(default=0.5, init=False)

    # Mate score value (used to represent mate in N moves as a centipawn score)
    mate_value: float = field(default=1000.0, init=False)

    # Table name for database storage
    table_name: str = field(default="chess_reporter.evaluation_parameter", init=False)
