# DECISIONS.md

## Project Overview

Chess Reporter is a personal portfolio project born from a genuine passion for chess, software engineering, and data architecture.

The goal is to perform cold, objective analysis of chess games and openings — free from emotion or bias. Every move is evaluated by Stockfish and assigned an accuracy score. Crucially, the analysis does not stop at the last move: the **termination context** is taken into account as part of the overall player score. For example:

- A player who **loses on time** but was in a winning position will have their accuracy penalized — the result does not reflect their play.
- A player who **accepts a draw** while holding a clear advantage will also be penalized — leaving a win on the board is a decision, and decisions are measured.
- Conversely, a player who **loses from a lost position** is not unfairly punished by the termination itself.

This approach produces a more honest and complete picture of how well each player actually played, beyond just the final result.

The project also serves as a showcase of the author's passion for chess, architecture, and engineering — combining domain knowledge with modern tooling into something that is both useful and maintainable.

---

This document captures the architectural and tooling decisions made throughout the project, along with the reasoning behind each choice.

---

## Language & Runtime

### Python
Python was chosen for its accessibility, rich ecosystem, and lack of a compilation step. It has strong support for chess libraries (e.g., `python-chess`), data processing, and analytical workloads. Python has also been maturing rapidly in terms of performance and type safety, making it a reliable choice for long-term projects.

### uv
`uv` replaces `pip` and `virtualenv` as the dependency and environment manager. It provides deterministic dependency resolution, faster installs, and cleaner version control — making it easier to reproduce environments across local development, CI, and Docker.

---

## Chess Engine

### Stockfish + ChessEngineManager + PositionManager

Stockfish is the strongest open-source chess engine available and serves as the analysis backbone of the project.

**Why run N times in parallel?**
Early testing revealed that running the same position once could produce slightly different evaluations across runs — non-determinism inherent to Stockfish's internal search. To address this, `ChessEngineManager` spawns `N` engine instances (always an odd number, default `5`) and runs them in parallel via `ThreadPoolExecutor` + `asyncio`. The results are aggregated into a **median** (used as the definitive score), **minimum**, and **maximum** — giving a statistical picture of the evaluation rather than a single potentially noisy value. The odd number of runs guarantees a clean median with no ambiguity.

**Why the median?**
The median is more robust than the mean against outliers. It is the value that will be used to compute move accuracy — by comparing the median eval before and after a move, a score between 0 and 100% (float) will be assigned to each move. The min/max values are preserved for future features.

**Avoiding redundant analysis**
`PositionManager` coordinates `ChessEngineManager` and `Board` to ensure that positions are not re-analyzed unnecessarily — the same position with the same termination state is not re-evaluated. This avoids wasted compute and keeps analysis deterministic for caching and storage purposes.

**Validation against external sources**
Evaluations from this pipeline were compared against evals from chess.com and lichess.com across multiple positions. Results were consistent, validating the approach.

**Stability in Docker/Kubernetes**
After extensive testing, running Stockfish inside Docker and Kubernetes proved significantly more stable than running it natively on the host. Resource isolation, consistent CPU/memory allocation, and the absence of competing system processes all contributed to more reliable and reproducible evaluations. This was a key factor in adopting the containerized deployment model.

**Why 4 threads?**
The number of Stockfish threads was set to `4` based on empirical data from the [CCRL benchmark (Stockfish 18, 4CPU)](https://www.computerchess.org.uk/ccrl/4040/cgi/engine_details.cgi?match_length=30&print=Details&each_game=1&eng=Stockfish%2018%2064-bit%204CPU). CCRL (Computer Chess Rating Lists) is a well-established independent rating list that tests engines under controlled conditions. The data shows that Stockfish's playing strength scales significantly when going from 1 to 4 threads, but returns diminish beyond that point. 4 threads represents the sweet spot between analysis quality and resource consumption — strong enough to produce evaluations comparable to what chess.com and lichess use, without over-provisioning CPU in a containerized environment.

---

## Storage & Data

### DuckDB
DuckDB was chosen as the embedded analytical database (OLAP) for the project. Being serverless and file-based, it requires no infrastructure to run locally or in a container. A key motivation is the concept of **OpenData** — the ability to ship or publish the `.duckdb` file as a self-contained, open dataset that anyone can query directly, without needing a running database server.

### Pydantic
All configuration, domain models, and parameters are defined as Pydantic `BaseModel` classes. This provides runtime validation, clear contracts between components, and a single source of truth for defaults and paths.

---

## Code Quality

### Ruff
Ruff handles both linting and formatting in a single fast tool. It enforces code style, catches common mistakes, and keeps the codebase consistent across contributors.

### Pyright
Pyright performs static type checking. Combined with explicit type annotations on all variables and function signatures, it catches type errors at development time before they reach runtime.

### pre-commit
pre-commit runs ruff and pyright (plus YAML and whitespace checks) automatically before every commit, acting as a quality gate to prevent unreviewed code from being committed.

---

## Testing

### pytest
pytest is the testing framework and the backbone of the development loop. The test suite covers domain models, database operations, storage, and engine integration. Beyond just catching regressions, it makes it safe to evolve the codebase aggressively — new managers and features can be built with confidence that existing behaviour is not silently broken. Stockfish-dependent tests are automatically skipped when the binary is not present (e.g., in CI), keeping the suite green without compromising coverage where it matters.

---

## Infrastructure

### Docker
The full application environment — Python, Stockfish, and JupyterLab — is packaged in a multi-stage Docker image. This ensures reproducibility across machines and makes deployment to Kubernetes straightforward.

### Kubernetes
k8s was chosen with future scalability in mind. As the project grows and additional features or services are introduced, Kubernetes provides a clean foundation for running multiple components together with proper resource control and easy redeployment.

### GitHub — Repository, Actions & Packages

The project lives in a **public GitHub repository**. Being public is intentional — it is part of the portfolio purpose. The code, decisions, and architecture are open for anyone to read, fork, or learn from.

**GitHub Actions** automates the CI pipeline. On every push, the workflow installs dependencies via `uv` and runs the full test suite. Stockfish-dependent tests are skipped in CI since the binary is not available in the runner — but the rest of the suite (domain, database, storage, utils) runs in full. This keeps the feedback loop fast and reliable without requiring a chess engine in the cloud.

**GitHub Packages (GHCR)** hosts the Docker image. After every release, the image is built locally and pushed to `ghcr.io/nielsencampos/chess-reporter:latest`. Kubernetes then pulls from GHCR on rollout — keeping the deployment simple and the image registry co-located with the source code, under the same GitHub account. No external registry needed.

---

## Developer Experience

### JupyterLab
JupyterLab serves as the primary interface for chess analysis and data exploration. It runs inside the Docker container and is exposed via Kubernetes, making it accessible from the browser without any local setup.

### Claude Code
Claude Code is used as a development accelerator — assisting with architecture decisions, code generation, commit messages, and deployments. It is treated as a collaborative engineering partner, not a replacement for design thinking.

### loguru
loguru handles structured logging with minimal boilerplate. Logs are written to stdout and to rotating files under `logs/`, making them accessible both in development and inside containers.

### sqlglot
sqlglot is used to parse and validate SQL before it reaches DuckDB. It classifies query types (DQL, DML, DDL, DCL) and ensures only well-formed SQL is executed.

---

## Versioning

Versions follow a `MAJOR.MINOR.PATCH` pattern and are tagged in git. Each minor version represents a meaningful milestone in the project's evolution.

| Version | Highlights |
|---------|------------|
| `v0.1.x` | Initial project structure — DuckDB, storage layer, Stockfish wrapper, JupyterLab in Docker/k8s. |
| `v0.2.x` | Full test suite, standardized code style, Stockfish install scripts, CI pipeline, `DECISIONS.md`. |
| `v0.3.x` _(planned)_ | MoveManager, GameManager, PGN parsing, ECO openings ingestion. |

---

## Roadmap

The project evolves incrementally as the understanding of cold chess analysis deepens. Below are the planned next steps following the stabilization and documentation phase (`v0.2.x`).

### New Managers

- **MoveManager** — responsible for processing individual moves within a game, computing per-move accuracy from sequential Stockfish evaluations (median before and after each move), and classifying moves on a 0–100% float scale.
- **GameManager** — orchestrates the full game pipeline: ingesting a PGN, running all positions through the engine, applying termination context penalties, and producing a complete game report per player.

### PGN Parsing

PGN (Portable Game Notation) is the universal raw format for chess games and will be the primary data input of the pipeline. A dedicated parser will be developed to extract structured data from PGN files — moves, metadata (players, date, result, time control), and termination type — feeding it into the analysis pipeline.

### ECO Openings

Chess openings are classified under the **ECO (Encyclopedia of Chess Openings)** system. The full dataset of known openings is publicly available from Lichess:

```
https://api.github.com/repos/lichess-org/chess-openings/contents/
```

The files are in TSV format and will be downloaded, processed, and stored in DuckDB. This will allow the pipeline to identify the opening played in each game and provide context on whether it was a sound or dubious choice — evaluated against Stockfish's assessment of the resulting positions.

### Philosophy

This is a project that grows with knowledge. As the understanding of how to objectively measure chess quality evolves — move by move, opening by opening, termination by termination — so does the pipeline. There is no fixed endpoint: every new insight about chess analysis becomes a new feature.
