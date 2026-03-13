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

### Stockfish (local development)

The binary lives in `bin/` (gitignored). Path is resolved by `src/chess_reporter/utils/find_engine.py:find_engine`, used as the `default_factory` for `ChessEngineParameters.path`.

Install scripts (run from the project root):

```powershell
# Windows
.\scripts\install_stockfish_win.ps1
```

```bash
# Linux / macOS (builds from source — requires g++ or clang++)
bash scripts/install_stockfish_unix.sh
```

## Architecture

The application is a chess game analysis pipeline using Stockfish + DuckDB, exposed via JupyterLab.

### Module structure under `src/chess_reporter/`

- **`bootstrap.py`** — Entry point for initializing storage and database. Calls `setup_logger` from `utils/setup_logger.py` when run as `__main__`.
- **`chess_domain/`** — Domain enums and Pydantic models, one file per type: `ScoreType`, `TurnType`, `TerminationType`, `ResultType`, `ClassificationType`, `PositionSetup`, `EngineSetup`, `MoveComment`, `MoveCommentElement`, `MoveCommentTitleType`.
- **`chess_engine/`** — Stockfish wrapper. `ChessEngineManager` runs N `ChessEngineInstance` evaluations sequentially (default `evaluation_runs=5`, must be odd) — parallel runs produce identical results, so series execution is used to preserve variability. Results are aggregated for robustness.
- **`position/`** — `PositionManager` coordinates a `ChessEngineManager` + `Board` to analyze a position. Validates consistency between `TerminationType` and `ResultType`.
- **`database/`** — `DatabaseManager` wraps DuckDB at `data/database/main.duckdb`. Parses SQL via `sqlglot` (dialect: `duckdb`), classifies query types (DQL/DML/DDL/DCL), returns `Query` domain objects. SQL schema/table definitions live in `database/sqls/`.
- **`storage/`** — File system layer for PGN/XLSX/CSV/JSON inputs and outputs. Root at `data/storage/{input,output}/{openings,games,others}/`.
- **`utils/`** — Shared utilities: `setup_logger.py` (loguru, stdout + rotating file in `logs/`), `generate_hash_id.py` (SHA-512 hash from list of values), `find_engine.py` (resolves Stockfish binary path via `PATH`, common locations, and `bin/` fallback).
- **`_scripts/`** — Internal CLI scripts registered in `pyproject.toml` (currently `clean`).

### Key design patterns

- All configuration uses **Pydantic `BaseModel`** with `Field` defaults. Parameters classes are the single source of truth for paths, table names, and engine settings.
- Each manager follows a **lifecycle pattern**: instantiate → use → `close()`. Always call `close()` to release Stockfish processes and thread pools.
- Database paths and storage paths are relative to the working directory (defaults: `data/database/main.duckdb`, `data/storage/`). In Docker/k8s, `/app/data` is a mounted PVC.

### Code style conventions (tests and src)

- **Imports**: always import only what is used — prefer `from module import Foo` over `import module`. Example: `from pytest import raises, fixture` instead of `import pytest`.
- **Type annotations**: annotate all local variables explicitly. Example: `board: Board = Board()`, `q: Query = _make_query(sql)`.
- **Docstrings**: multi-line style with a blank line after the opening `"""` and before the closing `"""`:
  ```python
  def foo() -> None:
      """
      Does something.
      """
  ```
- **Spacing**: always add a blank line before `assert`, `return`, `with raises`, and `yield` statements to keep things readable and not cramped.
- **Guard assertions**: use `assert x is not None` instead of `# type: ignore` when narrowing types — fails loudly at runtime and satisfies Pyright.

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
