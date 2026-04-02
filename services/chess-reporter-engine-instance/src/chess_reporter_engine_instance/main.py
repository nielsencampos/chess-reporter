"""
Engine instance: FastAPI application.
"""

from __future__ import annotations

from fastapi import FastAPI

from .routers import health, run, specs

app: FastAPI = FastAPI(
    title="Chess Reporter: Engine Instance",
    description=(
        "A microservice that runs a chess engine (e.g. Stockfish) and exposes an API "
        "for analyzing chess positions."
    ),
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(run.router)
app.include_router(specs.router)
