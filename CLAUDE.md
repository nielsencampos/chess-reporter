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

The binary lives in `bin/` (gitignored). Path is resolved by `src/chess_reporter/utils/find_engine.py:find_engine`, used as the `default_factory` for `EngineParameters.path`.

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

- **`bootstrap.py`** — Entry point. Calls `StorageBootstrapper().bootstrap()` and `DatabaseBootstrapper().bootstrap()`. Calls `setup_logger` from `utils/setup_logger.py` when run as `__main__`.

- **`domain/`** — All domain types, organized by subdomain. Each subdomain has its own `__init__.py`. The top-level `domain/__init__.py` is intentionally bare — import from specific submodules directly.
  - **`domain/data/`** — `DataStatus(StrEnum)`: PENDING, IN_PROGRESS, COMPLETED, FAILED. Each value has `.priority`, `.name` (human-readable display name), `.description`.
  - **`domain/game/`** — `GameResult(StrEnum)`, `GameTermination(StrEnum)`, `GameOutcome(BaseModel, frozen)`, `GamePhase(StrEnum)`. `GameOutcome` validates that result and termination agree on `is_finished`, `has_winner`, `is_draw`.
  - **`domain/move/`** — `MoveClassification(StrEnum)` (11 categories: BOOK → BRILLIANT), `MoveType(StrEnum)` (PLAYED/MAINLINE/VARIATION), `MoveCommentTitle(StrEnum)`, `MoveCommentElement(BaseModel)`, `MoveComment(RootModel)` (parses/serializes PGN `{[%tag value]}` comments), `MoveContext(BaseModel, frozen)` (board_before + move → SAN, UCI, capture/castling/promotion flags, board_after).
  - **`domain/position/`** — `PositionTurn(StrEnum)`, `PositionMaterialInfo(BaseModel, frozen)`, `PositionLegalMoves(RootModel[list[MoveContext]], frozen)`, `PositionContext(BaseModel, frozen)`. Standalone builder functions: `get_position_game_outcome_from_board`, `get_position_material_info_from_board`, `get_position_legal_moves_from_board`. Material values: PAWN=100, KNIGHT/BISHOP=300, ROOK=500, QUEEN=900 (kings counted but not valued). Game phase by total piece count: ≥26 OPENING, ≥12 MIDDLEGAME, else ENDGAME.
  - **`domain/engine/`** — `EngineAnalysis(BaseModel)`, `EngineContext(BaseModel, frozen)`, `EngineEvaluationType(StrEnum)` (NORMAL/FAILED/FORCED), `EngineScoreType(StrEnum)` (CENTIPAWNS/MATE). Builder functions: `build_engine_variation_moves`, `build_engine_refutation_moves`, `build_engine_current_line_moves` (all delegate to shared `build_move_sequence` helper). `EngineContext` exposes `.board` (copy with `stack=False`) and `.game_outcome` as `@cached_property`. `EngineAnalysis` key computed fields: `evaluation` (formatted string), `score_type`, `score_value`, `score_in_centipawns`, `win_probability_balance`, `hash_table_usage` (hashfull per-mille → %), `time_in_seconds`, `evaluation_type`, `variation_rank`, `search_depth`, `selective_search_depth`, `ebf`, `message`.

- **`engine/`** — Stockfish wrapper.
  - `EngineParameters(BaseModel, frozen)` — path, threads=4, hash_table_mb=4096, depth=30, multipv=7, analyses=7 (must be odd), parallelism=True, engine_config_table="chess_reporter.engine_config".
  - `EngineConfigData(BaseModel)` — serializable snapshot of engine config (name_version, threads, hash_table_mb, depth, multipv, analyses, parallelism) with SHA-512 hash ID, saved to `chess_reporter.engine_config` on init.
  - `EngineInstance` — wraps one `SimpleEngine`. Context manager. `get_analyses() -> list[EngineAnalysis]`. Passing `context=None` opens and immediately closes (used for config probing in `EngineManager.__init__`).
  - `EngineManager` — orchestrates N analysis runs for a `PositionContext`. `parallelism=False` → sequential loop; `parallelism=True` → queue-based workers (`_get_max_workers()` = `max(1, logical_cpus_available // threads)`).

- **`database/`** — `DatabaseManager` wraps DuckDB at `data/database/main.duckdb`. Parses SQL via `sqlglot` (dialect: `duckdb`), classifies DQL/DML/DDL/DCL, returns `Query` domain objects. SQL files live in `database/sql/schema/` and `database/sql/table/` (executed in sorted filename order by `DatabaseBootstrapper`). `Table(RootModel[str])` validates `schema.table` format; `.is_internal` is True when schema is `chess_reporter`. Only `DatabaseManager(internal=True)` can call `.merge()` on internal tables; `.create_table()` and `.insert()` are forbidden for internal tables.

- **`storage/`** — File system layer. Root at `data/storage/{input,output}/{opening,game,other}/`. `StorageBootstrapper` creates all folders on startup. `StorageManager` reads (bytes for binary, str for text), saves, and deletes files. Valid extensions: `parquet`, `pgn`, `xlsx` (binary); `json` (text).

- **`utils/`** — Shared utilities: `setup_logger.py` (loguru, stdout + rotating file in `logs/`), `generate_hash_id.py` (SHA-512 hash from list of values), `find_engine.py` (resolves Stockfish binary path via `PATH`, common locations, and `bin/` fallback), `get_logic_cpu_available.py` (logical CPUs available based on current usage, 1s sampling interval). The top-level `utils/__init__.py` is intentionally bare — import from specific submodules directly.

- **`_scripts/`** — Internal CLI scripts registered in `pyproject.toml` (currently `clean`).

### Key design patterns

- All configuration uses **Pydantic `BaseModel`** with `Field` defaults. Parameters classes are the single source of truth for paths, table names, and engine settings.
- **`RootModel`** is used for list/string wrappers: `MoveComment(RootModel[list[MoveCommentElement]])`, `PositionLegalMoves(RootModel[list[MoveContext]])`, `Table(RootModel[str])`.
- **Frozen models** (`ConfigDict(frozen=True)`) are used for domain value objects (`MoveContext`, `PositionContext`, `EngineContext`, `GameOutcome`, etc.).
- **`@computed_field @cached_property`** is used for serializable derived values that are expensive to compute. Pydantic v2 supports `cached_property` on frozen models (writes to `__dict__` directly, bypassing `__setattr__`).
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
- **Type syntax**: use `str | None` instead of `Optional[str]`, and builtin generics (`list[str]`, `dict[str, int]`, `tuple[int, ...]`) instead of `typing.List`, `typing.Dict`, `typing.Tuple`.

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
