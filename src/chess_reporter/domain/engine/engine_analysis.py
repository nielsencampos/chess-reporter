"""
Chess domain: Engine analysis module
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import cached_property

from chess import BLACK, WHITE, Board, Move
from chess.engine import Cp, InfoDict, Mate, PovScore, PovWdl, Wdl
from pydantic import BaseModel, ConfigDict, Field, computed_field

from chess_reporter.domain.game import GameResult
from chess_reporter.domain.move import MoveContext

from .build_engine_current_line_moves import build_engine_current_line_moves
from .build_engine_refutation_moves import build_engine_refutation_moves
from .build_engine_variation_moves import build_engine_variation_moves
from .engine_context import EngineContext
from .engine_evaluation_type import EngineEvaluationType
from .engine_score_type import EngineScoreType


class EngineAnalysis(BaseModel):
    """
    Engine Analysis
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    context: EngineContext = Field(
        description="Engine context for which the result is being reported"
    )
    started_analysis_at: datetime = Field(
        description="Timestamp indicating when started the analysis for the run",
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp indicating when finished the analysis for the run",
        default_factory=lambda: datetime.now(timezone.utc),
        frozen=True,
    )
    info_dict: InfoDict = Field(
        description="Information dictionary containing the analysis results from the engine",
    )
    mate_in_centipawns: int = Field(
        description="Centipawn equivalent of a mate score",
        default=100000,
        frozen=True,
    )

    @computed_field
    @property
    def analysis_run(self) -> int:
        """
        Analysis run number
        """
        return self.context.analysis_run

    @property
    def board(self) -> Board:
        """
        Board position for which the analysis was performed
        """
        return self.context.position_context.board

    @property
    def ply(self) -> int:
        """
        Ply for which the analysis was performed
        """
        return self.board.ply()

    @property
    def is_finished(self) -> bool:
        """
        Whether the game is finished
        """
        return self.context.game_outcome.is_finished

    @property
    def has_winner(self) -> bool:
        """
        Whether the game has a winner
        """
        return self.context.game_outcome.has_winner

    @property
    def is_draw(self) -> bool:
        """
        Whether the game is a draw
        """
        return self.context.game_outcome.is_draw

    @property
    def is_white_winner(self) -> bool:
        """
        Whether white is the winner
        """
        return self.context.game_outcome.game_result == GameResult.WHITE_WON

    @property
    def is_black_winner(self) -> bool:
        """
        Whether black is the winner
        """
        return self.context.game_outcome.game_result == GameResult.BLACK_WON

    @computed_field
    @cached_property
    def variation_rank(self) -> int:
        """
        Variation rank (multipv)
        """
        return self.info_dict.get("multipv", 1)

    @computed_field
    @cached_property
    def evaluation_type(self) -> EngineEvaluationType:
        """
        Evaluation type
        """
        if self.is_finished:
            return EngineEvaluationType.FORCED

        if self.info_dict.get("score") is None:
            return EngineEvaluationType.FAILED

        return EngineEvaluationType.NORMAL

    @cached_property
    def pov_score(self) -> PovScore:
        """
        POV score from the engine evaluation
        """
        if self.has_winner:
            return PovScore(Mate(0), WHITE if self.is_white_winner else BLACK)

        if self.is_draw:
            return PovScore(Cp(0), WHITE)

        engine_pov_score: PovScore | None = self.info_dict.get("score")

        return engine_pov_score if engine_pov_score is not None else PovScore(Cp(0), WHITE)

    @cached_property
    def pov_wdl(self) -> PovWdl:
        """
        POV Win/draw/loss probability from the engine evaluation
        """
        if self.has_winner:
            return PovWdl(Wdl(1000, 0, 0), WHITE if self.is_white_winner else BLACK)

        if self.is_draw:
            return PovWdl(Wdl(0, 1000, 0), WHITE)

        engine_pov_wdl: PovWdl | None = self.info_dict.get("wdl")

        return (
            engine_pov_wdl
            if engine_pov_wdl is not None
            else self.pov_score.wdl(
                model="sf16",
                ply=self.ply,
            )
        )

    @cached_property
    def pv_moves(self) -> list[Move]:
        """
        Variation moves (pv)
        """
        return self.info_dict.get("pv", [])

    @cached_property
    def refutation(self) -> dict[Move, list[Move]]:
        """
        Refutation moves (refutation)
        """
        return self.info_dict.get("refutation", {})

    @computed_field
    @cached_property
    def search_depth(self) -> int:
        """
        Search depth at which the chess engine evaluation was performed
        """
        return self.info_dict.get("depth", 0)

    @computed_field
    @cached_property
    def selective_search_depth(self) -> int:
        """
        Selective search depth at which the chess engine evaluation was performed
        """
        return self.info_dict.get("seldepth", 0)

    @computed_field
    @cached_property
    def total_positions_evaluated(self) -> int:
        """
        Total number of positions evaluated during the search
        """
        return self.info_dict.get("nodes", 0)

    @computed_field
    @cached_property
    def nodes_per_second(self) -> int:
        """
        Number of positions evaluated per second
        """
        return self.info_dict.get("nps", 0)

    @computed_field
    @cached_property
    def ebf(self) -> float:
        """
        Effective branching factor of the search
        """
        engine_ebf: float | None = self.info_dict.get("ebf")

        if engine_ebf is not None:
            return float(engine_ebf)

        nodes: float = float(self.total_positions_evaluated)
        depth: float = float(self.search_depth)

        if nodes <= 0.0 or depth <= 0.0:
            return 0.0

        return nodes ** (1.0 / depth)

    @computed_field
    @cached_property
    def tablebase_hits(self) -> int:
        """
        Number of endgame tablebase lookups performed during the search
        """
        return self.info_dict.get("tbhits", 0)

    @computed_field
    @cached_property
    def cpu_load(self) -> int | None:
        """
        CPU load reported by the chess engine, if available
        """
        return self.info_dict.get("cpuload")

    @computed_field
    @cached_property
    def hash_table_usage(self) -> float:
        """
        Hash table usage percentage
        """
        value: float = float(self.info_dict.get("hashfull", 0))

        return value / 10.0

    @computed_field
    @cached_property
    def time_in_seconds(self) -> float:
        """
        Time in seconds spent by the engine during the search
        """
        return self.info_dict.get("time", 0.0)

    @computed_field
    @cached_property
    def message(self) -> str:
        """
        Informational message reported by the engine during the search
        """
        if self.evaluation_type == EngineEvaluationType.FORCED:
            return "*** Forced resolution detected. ***"

        engine_message: str | None = self.info_dict.get("string")

        if engine_message is not None:
            return engine_message

        return "*** No message reported by the engine. ***"

    @cached_property
    def current_line(self) -> dict[int, list[Move]]:
        """
        Current line (currline) reported by the engine during the search, if available.
        """
        return self.info_dict.get("currline", {})

    @cached_property
    def current_move_number(self) -> int | None:
        """
        Current move number (currmovenumber) reported by the engine during the search, if available.
        """
        return self.info_dict.get("currmovenumber")

    @cached_property
    def current_move(self) -> MoveContext | None:
        """
        Current move (currmove) reported by the engine during the search, if available.
        """
        move: Move | None = self.info_dict.get("currmove")

        if move is None:
            return None

        return MoveContext(
            board_before=self.board.copy(stack=False),
            move=move,
        )

    @computed_field
    @cached_property
    def score_type(self) -> EngineScoreType:
        """
        Score type
        """
        return EngineScoreType.MATE if self.pov_score.is_mate() else EngineScoreType.CENTIPAWNS

    @computed_field
    @cached_property
    def score_value(self) -> int:
        """
        Score value
        """
        if self.pov_score.is_mate():
            mate_value: int | None = self.pov_score.white().mate()

            return mate_value if mate_value is not None else 0

        centipawns_value: int | None = self.pov_score.white().score()

        return centipawns_value if centipawns_value is not None else 0

    @computed_field
    @cached_property
    def score_in_centipawns(self) -> int:
        """
        Score in centipawns
        """
        if self.score_type == EngineScoreType.CENTIPAWNS:
            return self.score_value

        if self.score_value == 0:
            return self.mate_in_centipawns if self.is_white_winner else -self.mate_in_centipawns

        mate_distance: int = abs(self.score_value)
        mate_score: int = self.mate_in_centipawns - mate_distance

        return mate_score if self.score_value > 0 else -mate_score

    @computed_field
    @cached_property
    def evaluation(self) -> str:
        """
        Evaluation string representing the engine evaluation in a human-readable format
        """
        if self.is_draw:
            return "1/2-1/2"

        if self.is_white_winner:
            return "1-0"

        if self.is_black_winner:
            return "0-1"

        if self.score_type == EngineScoreType.CENTIPAWNS:
            if self.score_value == 0:
                return "0.00"

            float_value: float = float(abs(self.score_value)) / 100.0
            str_value: str = f"{float_value:.2f}"

            return f"+{str_value}" if self.score_value > 0 else f"-{str_value}"

        return f"+#{self.score_value}" if self.score_value > 0 else f"-#{self.score_value}"

    @computed_field
    @cached_property
    def win_probability_balance(self) -> float:
        """
        Win probability balance, the difference in winning chances between white and black
        """
        white_pov_wdl: Wdl = self.pov_wdl.white()
        white_win_prob: float = white_pov_wdl.wins / 1000.0
        white_draw_prob: float = white_pov_wdl.draws / 1000.0
        white_loss_prob: float = white_pov_wdl.losses / 1000.0

        expected_white: float = white_win_prob + 0.5 * white_draw_prob
        expected_black: float = white_loss_prob + 0.5 * white_draw_prob

        return (expected_white - expected_black) * 100.0

    @cached_property
    def variation_moves(self) -> list[MoveContext]:
        """
        Variation moves with their corresponding board positions for the engine analysis
        """
        return build_engine_variation_moves(self.board, self.pv_moves)

    @cached_property
    def refutation_moves(self) -> list[tuple[MoveContext, list[MoveContext]]]:
        """
        Refutation moves with their corresponding board positions for the engine analysis
        """
        return build_engine_refutation_moves(self.board, self.refutation)

    @cached_property
    def current_line_moves(self) -> list[tuple[int, list[MoveContext]]]:
        """
        Current line moves with their corresponding board positions for the engine analysis
        """
        return build_engine_current_line_moves(self.board, self.current_line)
