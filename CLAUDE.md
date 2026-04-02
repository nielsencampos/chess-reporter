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
uv run ruff check .
uv run ruff format .

# Type checking
uv run pyright

# Run tests
uv run pytest

# Pre-commit (runs ruff + pyright + yaml/whitespace checks)
uv run pre-commit run --all-files
```

### Stockfish (local development)

The binary lives in `bin/` (gitignored). Path is resolved by `services/chess-reporter/src/chess_reporter/utils/find_engine.py`.

Install scripts (run from the project root):

```powershell
# Windows
.\scripts\install_stockfish_win.ps1
```

```bash
# Linux / macOS
bash scripts/install_stockfish_unix.sh
```

## Project status

The project is in **active redevelopment** from a monolithic JupyterLab pipeline into a microservices architecture.

## Architecture

### Services

| Service | Path | Responsibility |
|---|---|---|
| chess-reporter | services/chess-reporter/ | Core domain logic (in development) |
| chess-reporter-engine-instance | services/chess-reporter-engine-instance/ | Stockfish FastAPI wrapper |
| chess-reporter-engine-master | services/chess-reporter-engine-master/ | Fan-out orchestrator |
| chess-reporter-jupyter-lab | services/chess-reporter-jupyter-lab/ | JupyterLab environment |
| chess-reporter-schemas | services/chess-reporter-schemas/ | Shared Pydantic schemas |

### engine-instance

FastAPI service wrapping one Stockfish process. Routers pattern - one file per endpoint under `routers/`.

- `routers/health.py` - GET /health
- `routers/run.py` - POST /run (async job pattern)
- `routers/specs.py` - GET /specs
- `core.py` - engine lifecycle, analysis
- `settings.py` - Pydantic BaseSettings, env prefix ENGINE\_
- `builders/` - payload construction from InfoDict
- `utils/` - find\_engine

Async job pattern in `routers/run.py`: module-level `_current_fen`, `_current_status`, `_current_payloads` protected by `threading.Lock`. BackgroundTasks runs analysis after response is returned.

### engine-master

FastAPI service orchestrating fan-out.

- `main.py` - lifespan (scale up on start, scale to 0 on shutdown), /health, /run
- `core.py` - fan-out via ThreadPoolExecutor, StatefulSet scale via k8s API
- `settings.py` - Pydantic BaseSettings, env prefix ENGINE\_
- `utils/spawner.py` - Spawner class, creates/deletes Deployment + Service pairs

### chess-reporter-schemas

Shared Pydantic models. Imported by both instance and master.

- `api/` - APIHealthPayload, APIHealthStatusType, APIResponseStatusType
- `engine/` - EnginePayload, EngineRequest, EngineResponse, EngineAnalysisPayload, EngineTelemetryPayload, EngineVariationPayload, EngineTracingPayload, EngineInstanceSpecsPayload

### Port conventions

| Service | Internal port |
|---|---|
| chess-reporter-engine-master | 1000 |
| chess-reporter-engine-instance | 1999 (mask) / 1001-1023 (per instance) |
| chess-reporter-jupyter-lab | 8888 (NodePort 30888) |
| chess-reporter-postgresql | 5432 |

### Infrastructure

- k8s on Docker Desktop (Windows). Use PowerShell + inline replace for ${LOCAL_PATH} - never envsubst.
- engine-instance: StatefulSet + headless Service (clusterIP: None). DNS: chess-reporter-engine-instance-{n}.chess-reporter-engine-instance.chess-reporter.svc.cluster.local:1999
- engine-master: Deployment + ServiceAccount + Role + RoleBinding (get/patch statefulsets/scale)
- PostgreSQL: Deployment + PVC + Secret

### Environment files

- `.env.postgresql.local` - PostgreSQL credentials for local docker-compose
- `.env.k8s` - GITHUB_PAT for GHCR pull secret
- All .env* files are gitignored

## Code style conventions

- **Imports**: always import only what is used - prefer `from module import Foo` over `import module`
- **Type annotations**: annotate all local variables explicitly
- **Docstrings**: multi-line style with a blank line after the opening `` and before the closing ``
- **Spacing**: always add a blank line before `assert`, `return`, `with raises`, and `yield` statements
- **Guard assertions**: use `assert x is not None` instead of `# type: ignore` when narrowing types
- **Type syntax**: use `str | None` instead of `Optional[str]`, and builtin generics (`list[str]`, `dict[str, int]`)
- **Unreachable**: use `raise RuntimeError("unreachable")` after try/except blocks to satisfy Pyright
- **Logging**: `logger.info` for entry points, `logger.debug` for responses, `logger.warning` for rejections, `logger.error` for failures

## BPR - Build, Push and Run

```powershell
# engine-instance
docker build -f docker/chess-reporter-engine-instance.Dockerfile -t ghcr.io/nielsencampos/chess-reporter-engine-instance:latest .
docker push ghcr.io/nielsencampos/chess-reporter-engine-instance:latest

# engine-master
docker build -f docker/chess-reporter-engine-master.Dockerfile -t ghcr.io/nielsencampos/chess-reporter-engine-master:latest .
docker push ghcr.io/nielsencampos/chess-reporter-engine-master:latest

# jupyter-lab
docker build -f docker/chess-reporter-jupyter-lab.Dockerfile -t ghcr.io/nielsencampos/chess-reporter-jupyter-lab:latest .
docker push ghcr.io/nielsencampos/chess-reporter-jupyter-lab:latest

# Restart deployments
kubectl rollout restart deployment/chess-reporter-engine-master --namespace chess-reporter
kubectl rollout restart statefulset/chess-reporter-engine-instance --namespace chess-reporter
```
