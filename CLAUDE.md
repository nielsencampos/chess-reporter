# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv`. The project requires Python 3.13+.

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Run linting and formatting
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run pyright

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_dummy.py

# Clean generated data
uv run clean

# Pre-commit (runs ruff + pyright + yaml/whitespace checks)
uv run pre-commit run --all-files
```

### Stockfish (local development on Windows)
The binary is at `bin/stockfish.exe`. The path is resolved via `STOCKFISH_PATH` env var or auto-detected by `src/chess_reporter/utils/utils.py:get_chess_engine_path`.

## Architecture

The application is a chess game analysis pipeline using Stockfish + DuckDB, exposed via JupyterLab.

### Module structure under `src/chess_reporter/`

- **`bootstrap.py`** — Entry point for initializing storage and database. Sets up loguru logger (stdout + rotating file in `logs/`).
- **`chess_domain/`** — Pure domain enums: `ScoreType`, `TurnType`, `TerminationType`, `ResultType`. No external dependencies.
- **`chess_engine/`** — Stockfish wrapper. `ChessEngineManager` spawns N `ChessEngineInstance` objects (default `evaluation_runs=5`, must be odd) and runs them in parallel via `ThreadPoolExecutor` + `asyncio`. Results are aggregated for robustness.
- **`position/`** — `PositionManager` coordinates a `ChessEngineManager` + `Board` to analyze a position. Validates consistency between `TerminationType` and `ResultType`.
- **`database/`** — `DatabaseManager` wraps DuckDB at `data/database/main.duckdb`. Parses SQL via `sqlglot` (dialect: `duckdb`), classifies query types (DQL/DML/DDL/DCL), returns `Query` domain objects. SQL schema/table definitions live in `database/sqls/`.
- **`storage/`** — File system layer for PGN/XLSX/CSV/JSON inputs and outputs. Root at `data/storage/{input,output}/{openings,games,others}/`.
- **`_scripts/`** — Internal CLI scripts registered in `pyproject.toml` (currently `clean`).

### Key design patterns

- All configuration uses **Pydantic `BaseModel`** with `Field` defaults. Parameters classes are the single source of truth for paths, table names, and engine settings.
- Each manager follows a **lifecycle pattern**: instantiate → use → `close()`. Always call `close()` to release Stockfish processes and thread pools.
- Database paths and storage paths are relative to the working directory (defaults: `data/database/main.duckdb`, `data/storage/`). In Docker/k8s, `/app/data` is a mounted PVC.

### Infrastructure

- **Docker**: `docker/chess-reporter.Dockerfile` — multi-stage build (Stockfish from source + uv Python). Runtime CMD is `jupyter lab` on port 8888.
- **Kubernetes**: `k8s/chess-reporter.yaml` — Service (NodePort 30888) + Deployment with hostPath volumes. JupyterLab accessible at `http://localhost:30888`.
- **Notebooks**: live in `notebooks/`, served by JupyterLab in the container.

## BPR — Build, Push & Run

Builds the Docker image, pushes to GHCR, and redeploys on k8s. Run in PowerShell.

```powershell
# 1. Build
docker build -f docker/chess-reporter.Dockerfile -t ghcr.io/nielsencampos/chess-reporter:latest .

# 2. Push
docker push ghcr.io/nielsencampos/chess-reporter:latest

# 3. Restart deployment (pulls the new latest)
kubectl rollout restart deployment/chess-reporter --namespace chess-reporter
kubectl rollout status deployment/chess-reporter --namespace chess-reporter
```

---

### Deploying locally (Windows)

Docker Desktop exposes Windows drives inside the k8s node at `/run/desktop/mnt/host/{drive}/...`. Always use PowerShell to apply the k8s manifest — **never** `envsubst` on Windows (it passes `D:/...` paths that Docker misparsed as bind mount mode):

```powershell
# Recreate secret after namespace delete
kubectl create secret docker-registry ghcr-secret `
  --namespace chess-reporter `
  --docker-server=ghcr.io `
  --docker-username=nielsencampos `
  --docker-password=<GITHUB_PAT>

# Apply manifest
(Get-Content .\k8s\chess-reporter.yaml -Raw) `
  -replace '\$\{LOCAL_PATH\}', '/run/desktop/mnt/host/d/projects/chess-reporter' `
  | kubectl apply -f -
```
