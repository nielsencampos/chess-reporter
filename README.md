# Chess Reporter

Chess game analysis pipeline using Stockfish and DuckDB, explored via JupyterLab.

## What it does

Chess Reporter processes PGN files and analyses each position using the Stockfish engine. Multiple Stockfish instances run in parallel (default: 5, always odd) and results are aggregated for robustness. Everything is stored in a DuckDB database and explored via JupyterLab notebooks.

**Current stage:** core analysis pipeline implemented — chess engine, position manager, database and storage layers are fully operational. JupyterLab is the primary interface for running analyses.

## Stack

| Layer | Technology |
|---|---|
| Chess engine | Stockfish 18 (compiled from source in Docker) |
| Database | DuckDB |
| Analysis | JupyterLab + Pandas |
| Validation | Pydantic |
| Runtime | Docker + Kubernetes |
| Package manager | uv (Python 3.13+) |

## Directory Structure

```
data/
  database/         # DuckDB (main.duckdb)
  storage/
    input/          # Input PGN, XLSX, CSV, JSON files
    output/         # Exported results
notebooks/          # Jupyter analysis notebooks
src/chess_reporter/
  chess_domain/     # Domain enums (ResultType, TerminationType, etc.)
  chess_engine/     # Stockfish wrapper with parallel execution
  position/         # Position analysis coordinator
  database/         # DuckDB manager
  storage/          # File system manager
  bootstrap.py      # Storage and database initialisation
  utils/            # Shared utilities
```

## Running locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / Mac / Linux)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (if using Kubernetes)
- Python 3.13+ and [uv](https://github.com/astral-sh/uv) (for development only)

---

### Option 1 — Docker (simplest)

Runs JupyterLab with your local `notebooks/` and `data/` folders mounted directly.

**Windows (PowerShell):**
```powershell
docker run --rm -it `
  -p 8888:8888 `
  -v "D:\projects\chess-reporter\notebooks:/app/notebooks" `
  -v "D:\projects\chess-reporter\data:/app/data" `
  ghcr.io/nielsencampos/chess-reporter:latest
```

**Mac / Linux:**
```bash
docker run --rm -it \
  -p 8888:8888 \
  -v "$(pwd)/notebooks:/app/notebooks" \
  -v "$(pwd)/data:/app/data" \
  ghcr.io/nielsencampos/chess-reporter:latest
```

Open the URL printed in the terminal (includes the token).

---

### Option 2 — Kubernetes (local)

The `k8s/chess-reporter.yaml` uses `${LOCAL_PATH}` as a variable for the host path. Substitute it before applying.

**Windows (PowerShell):**

> Docker Desktop exposes Windows drives inside the k8s node at `/run/desktop/mnt/host/{drive}/...`. Use that path, not the Windows path.

```powershell
(Get-Content .\k8s\chess-reporter.yaml -Raw) `
  -replace '\$\{LOCAL_PATH\}', '/run/desktop/mnt/host/d/projects/chess-reporter' `
  | kubectl apply -f -
```

**Mac / Linux:**
```bash
LOCAL_PATH=$(pwd) envsubst < k8s/chess-reporter.yaml | kubectl apply -f -
```

Then port-forward to access JupyterLab:
```bash
kubectl port-forward -n chess-reporter deployment/chess-reporter 8888:8888
```

Open `http://127.0.0.1:8888` and use the token from the pod logs:
```bash
kubectl logs -n chess-reporter deployment/chess-reporter | grep token=
```

---

## Development

```bash
# Install dependencies (including dev tools)
uv sync --group dev

# Lint and format
uv run ruff check src/
uv run ruff format src/

# Type check
uv run pyright

# Tests
uv run pytest

# Pre-commit (runs all checks)
uv run pre-commit run --all-files
```

## CI/CD

On every push, GitHub Actions:
1. Runs ruff, pyright and pytest
2. Builds the Docker image
3. Pushes to `ghcr.io/nielsencampos/chess-reporter:latest`

To deploy after a push:
```bash
kubectl rollout restart deployment/chess-reporter -n chess-reporter
```
