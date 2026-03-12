# Chess Reporter

> Cold, objective analysis of chess games and openings — free from emotion or bias.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-container-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-orchestration-326CE5?logo=kubernetes&logoColor=white)
![Chess](https://img.shields.io/badge/chess-analysis-8B4513?logo=lichess&logoColor=white)
![Open Data](https://img.shields.io/badge/open--data-reproducible-success)
![JupyterLab](https://img.shields.io/badge/JupyterLab-notebooks-F37626?logo=jupyter&logoColor=white)
![Software Architecture](https://img.shields.io/badge/software--architecture-explicit%20domain%20modeling-blueviolet)
![Stockfish](https://img.shields.io/badge/Stockfish-18-darkgreen?logo=lichess&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-claude--code-D97757?logo=anthropic&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000?logo=duckdb&logoColor=black)

Chess Reporter is a chess analysis pipeline built with Python and Stockfish that generates reproducible **open datasets** from objective engine evaluation. Born from a genuine passion for chess and data architecture, it evaluates every move using Stockfish, assigns an accuracy score per move, and — crucially — accounts for how the game ended.

A player who loses on time while winning gets penalized. A player who accepts a draw from a winning position gets penalized. The result alone does not tell the whole story — Chess Reporter does.

---

## Open Data

One of the goals of Chess Reporter is to generate reproducible **open datasets** derived from objective engine analysis.

Instead of keeping results locked behind a running service, the project stores analysis results directly in a portable DuckDB database.

This makes it possible to:

- share complete analysis datasets as a single file
- allow anyone to query the results locally
- encourage reproducible chess research and experimentation

---

## Product

The pipeline takes a PGN file as input and produces a complete game report:

- **Per-move accuracy** — each move is scored 0–100% based on Stockfish evaluations before and after
- **Termination context** — timeouts, resignations, draw agreements, and checkmates are all factored into the final player score
- **Opening identification** — games are matched against the ECO (Encyclopedia of Chess Openings) database from Lichess
- **Player report** — a full picture of how well each player actually played, regardless of result

Analysis is explored interactively via **JupyterLab**, and data is stored in **DuckDB** — a self-contained file that can be shared as an open dataset (OpenData), queryable by anyone without a database server.

---

## Architecture

The engine layer is designed for robustness, not just speed.

Stockfish is non-deterministic: the same position can produce slightly different evaluations across runs. However, running instances in parallel causes all runs to produce identical results, eliminating variability. To preserve the natural non-determinism of the engine, `ChessEngineManager` runs **N evaluations sequentially** (always an odd number, default 5). Results are aggregated into a **median** (the definitive score), **minimum**, and **maximum**.

The median was chosen over the mean for its resistance to outliers. The odd number of runs guarantees a clean median with no ambiguity.

Stockfish runs with **4 threads per instance**, chosen based on empirical data from the [CCRL benchmark (Stockfish 18, 4CPU)](https://www.computerchess.org.uk/ccrl/4040/cgi/engine_details.cgi?match_length=30&print=Details&each_game=1&eng=Stockfish%2018%2064-bit%204CPU) — the sweet spot between analysis quality and resource consumption.

The full stack:

| Layer | Technology |
|---|---|
| Chess engine | Stockfish 18 (compiled from source in Docker) |
| Engine orchestration | `ChessEngineManager` + `PositionManager` |
| Database | DuckDB (embedded OLAP, OpenData-ready) |
| Domain & validation | Pydantic |
| Analysis interface | JupyterLab |
| Runtime | Docker + Kubernetes |
| Package manager | uv (Python 3.13+) |

---

## Software

The codebase is structured around **Pydantic `BaseModel`** classes as the single source of truth for configuration, paths, and parameters. Each manager follows a lifecycle pattern: instantiate → use → `close()`.

Code quality is enforced via **Ruff** (lint + format), **Pyright** (static typing), and **pre-commit** hooks. All variables carry explicit type annotations. Tests follow a consistent style: granular imports, multi-line docstrings, and explicit spacing.

The test suite covers domain models, database operations, storage, and Stockfish integration — 63 tests, all passing. Engine tests are skipped automatically in environments without the binary (e.g., CI).

```
chess-reporter/
├── .github/
│   └── workflows/
│       └── ci.yml                        # GitHub Actions — lint, type check, tests
├── bin/                                  # Stockfish binary (gitignored)
├── data/                                 # Generated data (OpenData-ready)
│   ├── database/                         # DuckDB (main.duckdb)
│   └── storage/
│       ├── input/                        # PGN, XLSX, CSV, JSON inputs
│       └── output/                       # Exported results
├── docker/
│   └── chess-reporter.Dockerfile         # Multi-stage build (Stockfish + uv + JupyterLab)
├── k8s/
│   ├── chess-reporter.yaml               # Deployment + Service (NodePort 30888)
│   └── namespace.yaml
├── logs/                                 # Rotating log files (gitignored)
├── notebooks/
│   └── sandbox.ipynb                     # Interactive analysis notebook
├── scripts/
│   ├── install_stockfish_unix.sh         # Build Stockfish from source (Linux/macOS)
│   └── install_stockfish_win.ps1         # Install Stockfish (Windows)
├── src/chess_reporter/
│   ├── chess_domain/                     # Domain enums and Pydantic models
│   ├── chess_engine/                     # Stockfish wrapper — parallel N-run orchestration
│   ├── position/                         # Position analysis coordinator
│   ├── database/                         # DuckDB manager + SQL parsing via sqlglot
│   │   └── sqls/                         # schemas.sql, tables.sql
│   ├── storage/                          # File system manager (PGN, XLSX, CSV, JSON)
│   ├── utils/                            # Logging (loguru), hashing, engine path resolution
│   ├── _scripts/                         # Internal CLI scripts (clean)
│   └── bootstrap.py                      # Storage and database initialisation
├── tests/                                # Full test suite (63 tests)
├── CLAUDE.md                             # Claude Code instructions and conventions
├── DATA_DICTIONARY.md                    # Database schema documentation
├── DECISIONS.md                          # Architectural and tooling decisions
├── pyproject.toml
└── README.md
```

---

## Design Principles

- Objective analysis over subjective interpretation
- Reproducible computation
- Open datasets instead of locked services
- Explicit domain modeling

---

## Running locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / Mac / Linux)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (if using Kubernetes)
- Python 3.13+ and [uv](https://github.com/astral-sh/uv) (for development only)

---

### Option 1 — Docker (simplest)

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

**Windows (PowerShell):**

> Docker Desktop exposes Windows drives inside the k8s node at `/run/desktop/mnt/host/{drive}/...`.

```powershell
(Get-Content .\k8s\chess-reporter.yaml -Raw) `
  -replace '\$\{LOCAL_PATH\}', '/run/desktop/mnt/host/d/projects/chess-reporter' `
  | kubectl apply -f -
```

**Mac / Linux:**
```bash
LOCAL_PATH=$(pwd) envsubst < k8s/chess-reporter.yaml | kubectl apply -f -
```

Open `http://localhost:30888` or port-forward:
```bash
kubectl port-forward -n chess-reporter deployment/chess-reporter 8888:8888
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

---

## CI/CD

On every push, GitHub Actions installs dependencies and runs the full test suite. Engine-dependent tests are skipped in CI (no Stockfish binary in the runner).

The Docker image is built and pushed manually to GHCR after each release (BPR):

```powershell
docker build -f docker/chess-reporter.Dockerfile -t ghcr.io/nielsencampos/chess-reporter:latest .
docker push ghcr.io/nielsencampos/chess-reporter:latest
kubectl rollout restart deployment/chess-reporter --namespace chess-reporter
```

---

> See [DECISIONS.md](DECISIONS.md) for the full architectural and tooling rationale behind this project.
