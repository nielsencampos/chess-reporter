# Chess Reporter

Chess game analysis pipeline using Stockfish and DuckDB, explored via JupyterLab.

## Overview

Chess Reporter processes PGN files, analyzes each position with the Stockfish engine (running N instances in parallel for robustness) and stores the results in a DuckDB database. Data exploration and analysis is done via JupyterLab.

## Stack

| Layer | Technology |
|---|---|
| Chess engine | Stockfish 18 |
| Database | DuckDB |
| Analysis | JupyterLab + Pandas |
| Validation | Pydantic |
| Infra | Docker + Kubernetes |

## Directory Structure

```
data/
  database/       # DuckDB (main.duckdb)
  storage/
    input/        # Input PGN, XLSX, CSV, JSON files
    output/       # Exported results
notebooks/        # Jupyter analysis notebooks
src/chess_reporter/
  chess_domain/   # Domain enums (ResultType, TerminationType, etc.)
  chess_engine/   # Stockfish wrapper with parallel execution
  position/       # Position analysis
  database/       # DuckDB manager
  storage/        # File manager
```

## Development

Requires Python 3.13+ and [`uv`](https://github.com/astral-sh/uv).

```bash
# Install dependencies
uv sync --group dev

# Lint and format
uv run ruff check src/
uv run ruff format src/

# Type check
uv run pyright

# Tests
uv run pytest

# Pre-commit
uv run pre-commit run --all-files
```

### Stockfish (Windows)

The binary is available at `bin/stockfish.exe`. The path is resolved automatically or via the `STOCKFISH_PATH` environment variable.

## Docker

```bash
docker build -f docker/chess-reporter.Dockerfile -t chess-reporter .
docker run -p 8888:8888 chess-reporter
```

JupyterLab available at `http://localhost:8888`.

## Kubernetes

The deployment at `k8s/chess-reporter.yaml` provisions two PVCs:

- `chess-reporter-data` (8Gi) → `/app/data`
- `chess-reporter-notebooks` (8Gi) → `/app/notebooks`
