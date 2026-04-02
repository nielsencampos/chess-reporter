# Chess Reporter

> Cold, objective analysis of chess games and openings - free from emotion or bias.

> **Active redevelopment** - The project is being rebuilt from a monolithic JupyterLab pipeline into a microservices architecture. Core domain logic is preserved; infrastructure is being redesigned from the ground up.

Chess Reporter is a chess analysis pipeline built with Python and Stockfish that generates reproducible **open datasets** from objective engine evaluation. Born from a genuine passion for chess and data architecture, it evaluates every move using Stockfish, assigns an accuracy score per move, and crucially accounts for how the game ended.

---

## Architecture

The project is being rebuilt as a **microservices system** deployed on Kubernetes.

| Service | Responsibility |
|---|---|
| chess-reporter-engine-instance | Wraps a single Stockfish process, exposes /run and /health via FastAPI |
| chess-reporter-engine-master | Orchestrates fan-out to engine instances, scales StatefulSet on startup/shutdown |
| chess-reporter-jupyter-lab | JupyterLab environment for analysis and data exploration |
| chess-reporter-postgresql | PostgreSQL database for persisting analysis results |

### Engine layer

Each engine instance processes **one FEN at a time** using an async job pattern:

- POST /run accepts or rejects based on current state (IN_PROGRESS, COMPLETED, FAILED, REJECTED)
- Analysis runs via FastAPI BackgroundTasks - response returns immediately with IN_PROGRESS
- Client polls by re-sending the same FEN until status is COMPLETED
- State is protected by a threading.Lock for thread safety
- Security by interface - no open state endpoint; polling requires the original FEN

The master fans out to all instances in **parallel** via ThreadPoolExecutor, aggregating results across runs.

### Port conventions

| Service | Internal port |
|---|---|
| chess-reporter-engine-master | 1000 |
| chess-reporter-engine-instance | 1999 (mask) / 1001-1023 (per instance) |
| chess-reporter-jupyter-lab | 8888 (NodePort 30888) |
| chess-reporter-postgresql | 5432 |

### Full stack

| Layer | Technology |
|---|---|
| Chess engine | Stockfish 18 (compiled from source in Docker) |
| Engine API | FastAPI + uvicorn |
| Engine orchestration | engine-master (fan-out via ThreadPoolExecutor) |
| Async job pattern | FastAPI BackgroundTasks + module-level state + threading.Lock |
| Database | PostgreSQL (local) / RDS (AWS planned) |
| Domain and validation | Pydantic v2 |
| Schemas | chess-reporter-schemas (shared Pydantic models across services) |
| Analysis interface | JupyterLab |
| Container runtime | Docker + Kubernetes (StatefulSet, RBAC, headless services) |
| Package manager | uv (Python 3.13+) |

---

## Repository structure

```
chess-reporter/
+-- .github/workflows/ci.yml
+-- assets/
+-- docker/
|   +-- chess-reporter-engine-instance.Dockerfile
|   +-- chess-reporter-engine-master.Dockerfile
|   \-- chess-reporter-jupyter-lab.Dockerfile
+-- k8s/
|   +-- namespace.yaml
|   +-- chess-reporter-engine-instance.yaml      # StatefulSet + headless Service
|   +-- chess-reporter-engine-master.yaml        # Deployment + RBAC
|   +-- chess-reporter-jupyter-lab.yaml          # Deployment + NodePort 30888
|   \-- chess-reporter-postgresql.yaml           # Deployment + PVC + Secret
+-- scripts/
+-- services/
|   +-- chess-reporter/                          # Core domain logic (in development)
|   +-- chess-reporter-engine-instance/          # Stockfish FastAPI wrapper
|   +-- chess-reporter-engine-master/            # Fan-out orchestrator
|   +-- chess-reporter-jupyter-lab/              # JupyterLab environment
|   \-- chess-reporter-schemas/                  # Shared Pydantic schemas
+-- docker-compose.yml                           # postgresql + jupyter-lab (local dev)
+-- CLAUDE.md
+-- DECISIONS.md
\-- pyproject.toml                               # uv workspace
```

---

## Running locally

### Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl
- Python 3.13+ and uv

### PostgreSQL + JupyterLab (docker-compose)

Create .env.postgresql.local at the project root:

```env
DB=chess_reporter
USER=chess_reporter
PASSWORD=chess_reporter
URL=postgresql://chess_reporter:chess_reporter@localhost:5432/chess_reporter
```

Then:

```bash
docker-compose up chess-reporter-postgresql chess-reporter-jupyter-lab
```

### Kubernetes (local - Windows PowerShell)

```powershell
kubectl apply -f k8s/namespace.yaml

kubectl create secret docker-registry ghcr-secret `
  --namespace chess-reporter `
  --docker-server=ghcr.io `
  --docker-username=nielsencampos `
  --docker-password=$env:GITHUB_PAT

kubectl apply -f k8s/chess-reporter-postgresql.yaml
kubectl apply -f k8s/chess-reporter-engine-instance.yaml
kubectl apply -f k8s/chess-reporter-engine-master.yaml

(Get-Content .\k8s\chess-reporter-jupyter-lab.yaml -Raw) `
  -replace '$\{LOCAL_PATH\}', '/run/desktop/mnt/host/d/projects/chess-reporter' `
  | kubectl apply -f -
```

JupyterLab at http://localhost:30888.

---

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format .
uv run pyright
uv run pytest
uv run pre-commit run --all-files
```

---

## CI/CD

On every push, GitHub Actions runs lint, type check, and tests. Docker images are built and pushed to GHCR automatically:

- ghcr.io/nielsencampos/chess-reporter-engine-instance:latest
- ghcr.io/nielsencampos/chess-reporter-engine-master:latest
- ghcr.io/nielsencampos/chess-reporter-jupyter-lab:latest

---

## Design Principles

- Objective analysis over subjective interpretation
- Reproducible computation
- Open datasets instead of locked services
- **Domain-Driven Design** - chess domain is the core; infrastructure is built around it
- **Single responsibility** - each service, class, and function does one thing
- **Explicit state** - module-level state with threading.Lock; no hidden coupling
- **Security by interface** - no open state endpoints; polling requires the original FEN

---

> See [DECISIONS.md](DECISIONS.md) for the full architectural and tooling rationale.
