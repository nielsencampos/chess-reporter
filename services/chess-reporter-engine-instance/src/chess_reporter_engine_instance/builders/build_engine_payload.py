"""
Engine instance: build engine payload module.
"""

from __future__ import annotations

from datetime import UTC, datetime

from chess import Move
from chess.engine import InfoDict, PovScore, PovWdl
from chess_reporter_schemas.engine import (
    EngineAnalysisPayload,
    EnginePayload,
    EngineTelemetryPayload,
    EngineTracingPayload,
    EngineVariationPayload,
)

from .build_engine_analysis_payload import build_engine_analysis_payload
from .build_engine_telemetry_payload import build_engine_telemetry_payload
from .build_engine_tracing_payload import build_engine_tracing_payload
from .build_engine_variation_payload import build_engine_variation_payload


def build_engine_payload(
    engine_wdl_model: str,
    engine_instance: int,
    fen: str,
    started_analysis_at: datetime,
    info_dict: InfoDict,
    real_cpu_usage: float,
) -> EnginePayload:
    """
    Build engine payload containing the analysis, variation, telemetry, and tracing information.

    Args:
        engine_wdl_model (str): The name of the engine WDL model used for the analysis.
        engine_instance (int): The analysis run number for which the result is being reported.
        fen (str): FEN string representing the chess position before the analysis.
        started_analysis_at (datetime): The timestamp when the analysis started.
        info_dict (InfoDict): The info dictionary containing the engine analysis information.
        real_cpu_usage (float): Real CPU usage percentage measured during the analysis.

    Returns:
        EnginePayload:
            An instance of EnginePayload containing the analysis, variation, telemetry,
            and tracing information.
    """
    finished_analysis_at: datetime = datetime.now(UTC)
    pov_score: PovScore | None = info_dict.get("score")
    pov_wdl: PovWdl | None = info_dict.get("wdl")
    search_depth: int = info_dict.get("depth", 0)
    selective_search_depth: int = info_dict.get("seldepth", 0)

    analysis: EngineAnalysisPayload = build_engine_analysis_payload(
        fen=fen,
        engine_wdl_model=engine_wdl_model,
        pov_score=pov_score,
        pov_wdl=pov_wdl,
        search_depth=search_depth,
        selective_search_depth=selective_search_depth,
    )

    pv: list[Move] | None = info_dict.get("pv")
    refutation: dict[Move, list[Move]] | None = info_dict.get("refutation")

    variation: EngineVariationPayload = build_engine_variation_payload(
        fen=fen,
        pv=pv,
        refutation=refutation,
    )

    total_positions_evaluated: int = info_dict.get("nodes", 0)
    nodes_per_second: int = info_dict.get("nps", 0)
    raw_cpu_load: int | None = info_dict.get("cpuload")
    cpu_load: float = float(raw_cpu_load) / 10.0 if raw_cpu_load is not None else real_cpu_usage
    hash_table_usage: float = float(info_dict.get("hashfull", 0)) / 10.0
    time_in_seconds: float = info_dict.get("time", 0.0)
    tablebase_hits: int = info_dict.get("tbhits", 0)
    effective_branching_factor: float = info_dict.get("ebf", 0.0)
    message: str = info_dict.get("string", "*** No message provided by the engine ***")
    failed_analysis: bool = pov_score is None

    telemetry: EngineTelemetryPayload = build_engine_telemetry_payload(
        failed_analysis=failed_analysis,
        search_depth=search_depth,
        selective_search_depth=selective_search_depth,
        total_positions_evaluated=total_positions_evaluated,
        nodes_per_second=nodes_per_second,
        effective_branching_factor=effective_branching_factor,
        tablebase_hits=tablebase_hits,
        hash_table_usage=hash_table_usage,
        message=message,
        cpu_load=cpu_load,
        real_cpu_usage=real_cpu_usage,
        time_in_seconds=time_in_seconds,
        started_analysis_at=started_analysis_at,
        finished_analysis_at=finished_analysis_at,
        info_dict=info_dict,
    )

    currmovenumber: int | None = info_dict.get("currmovenumber")
    currmove: Move | None = info_dict.get("currmove")
    currline: dict[int, list[Move]] | None = info_dict.get("currline")

    tracing: EngineTracingPayload = build_engine_tracing_payload(
        fen=fen,
        currmovenumber=currmovenumber,
        currmove=currmove,
        currline=currline,
    )

    multipv: int = info_dict.get("multipv", 1)

    return EnginePayload(
        fen=fen,
        analysis_run=engine_instance,
        variation_rank=multipv,
        analysis=analysis,
        variation=variation,
        telemetry=telemetry,
        tracing=tracing,
    )
