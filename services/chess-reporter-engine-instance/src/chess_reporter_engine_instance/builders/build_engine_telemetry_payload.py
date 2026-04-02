"""
Engine instance: Build engine telemetry payload module
"""

from __future__ import annotations

from datetime import datetime

from chess.engine import InfoDict
from chess_reporter_schemas.engine import EngineTelemetryPayload

from .build_engine_raw_info_dict import build_engine_raw_info_dict


def build_engine_telemetry_payload(
    failed_analysis: bool,
    search_depth: int,
    selective_search_depth: int,
    total_positions_evaluated: int,
    nodes_per_second: int,
    effective_branching_factor: float,
    tablebase_hits: int,
    hash_table_usage: float,
    message: str,
    cpu_load: float,
    real_cpu_usage: float,
    time_in_seconds: float,
    started_analysis_at: datetime,
    finished_analysis_at: datetime,
    info_dict: InfoDict,
) -> EngineTelemetryPayload:
    """
    Build engine telemetry payload from the given parameters and the engine's info dictionary.

    Args:
        failed_analysis (bool): Indicates whether the engine analysis failed for the position.
        search_depth (int): Search depth for the analysis.
        selective_search_depth (int): Selective search depth for the analysis.
        total_positions_evaluated (int): Total positions evaluated during the analysis.
        nodes_per_second (int): Nodes per second during the analysis.
        effective_branching_factor (float): Effective branching factor (EBF) for the analysis.
        tablebase_hits (int): Number of tablebase hits during the analysis.
        hash_table_usage (float): Hash table usage percentage during the analysis.
        message (str): Informational message reported by the engine during the search.
        cpu_load (float): CPU load reported by the engine.
        real_cpu_usage (float): Real CPU usage percentage measured during the analysis.
        time_in_seconds (float): Time taken for the analysis in seconds.
        started_analysis_at (datetime): Timestamp when the analysis started.
        finished_analysis_at (datetime): Timestamp when the analysis finished.
        info_dict (InfoDict):
            Raw information dictionary containing the analysis results from the engine.

    Returns:
        EngineTelemetryPayload: The constructed engine telemetry payload.
    """

    return EngineTelemetryPayload(
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
        raw_info_dict=build_engine_raw_info_dict(info_dict),
    )
