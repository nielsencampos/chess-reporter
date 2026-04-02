# DECISIONS.md

## Project Overview

Chess Reporter is a personal portfolio project born from a genuine passion for chess, software engineering, and data architecture.

The goal is to perform cold, objective analysis of chess games and openings â€” free from emotion or bias. Every move is evaluated by Stockfish and assigned an accuracy score. Crucially, the analysis does not stop at the last move: the **termination context** is taken into account as part of the overall player score. For example:

- A player who **loses on time** but was in a winning position will have their accuracy penalized â€” the result does not reflect their play.
- A player who **accepts a draw** while holding a clear advantage will also be penalized â€” leaving a win on the board is a decision, and decisions are measured.
- Conversely, a player who **loses from a lost position** is not unfairly punished by the termination itself.

This approach produces a more honest and complete picture of how well each player actually played, beyond just the final result.

The project also serves as a showcase of the author's passion for chess, architecture, and engineering â€” combining domain knowledge with modern tooling into something that is both useful and maintainable.

---

This document captures the architectural and tooling decisions made throughout the project, along with the reasoning behind each choice.

---

## Language & Runtime

### Python
Python was chosen for its accessibility, rich ecosystem, and lack of a compilation step. It has strong support for chess libraries (e.g., `python-chess`), data processing, and analytical workloads. Python has also been maturing rapidly in terms of performance and type safety, making it a reliable choice for long-term projects.

### uv
`uv` replaces `pip` and `virtualenv` as the dependency and environment manager. It provides deterministic dependency resolution, faster installs, and cleaner version control â€” making it easier to reproduce environments across local development, CI, and Docker.

---

## Chess Engine

### Stockfish + EngineManager

Stockfish is the strongest open-source chess engine available and serves as the analysis backbone of the project.

**Why run N times in series?**
Early testing revealed that running the same position once could produce slightly different evaluations across runs â€” non-determinism inherent to Stockfish's internal search. However, when `N` engine instances were run in parallel, all runs produced identical results for the same position, eliminating any variability. Running the same position in series (one after another) was what actually produced different evaluations across runs, preserving the natural non-determinism of the engine. To address this, `EngineManager` runs `N` evaluations sequentially (always an odd number, default `5`). The results are aggregated into a **median** (used as the definitive score), **minimum**, and **maximum** â€” giving a statistical picture of the evaluation rather than a single potentially noisy value. The odd number of runs guarantees a clean median with no ambiguity.

**Why the median?**
The median is more robust than the mean against outliers. It is the value that will be used to compute move accuracy â€” by comparing the median eval before and after a move, a score between 0 and 100% (float) will be assigned to each move. The min/max values are preserved for future features.

**Avoiding redundant analysis**
Positions are not re-analyzed unnecessarily â€” the same position with the same termination state is not re-evaluated. This avoids wasted compute and keeps analysis deterministic for caching and storage purposes.

**Validation against external sources**
Evaluations from this pipeline were compared against evals from chess.com and lichess.com across multiple positions. Results were consistent, validating the approach.

**Stability in Docker/Kubernetes**
After extensive testing, running Stockfish inside Docker and Kubernetes proved significantly more stable than running it natively on the host. Resource isolation, consistent CPU/memory allocation, and the absence of competing system processes all contributed to more reliable and reproducible evaluations. This was a key factor in adopting the containerized deployment model.

**Why 4 threads?**
The number of Stockfish threads was set to `4` based on both empirical testing and external benchmarks. Thread counts from 1 to 12 were tested by comparing the resulting evaluations against known analyses from chess.com and lichess.com across multiple positions. `4` threads produced evaluations most consistent with those references. A notable finding: `2` threads performed worse than `1` thread â€” an unexpected result that reinforced the need for empirical validation rather than assuming linear scaling. This is also consistent with data from the [CCRL benchmark (Stockfish 18, 4CPU)](https://www.computerchess.org.uk/ccrl/4040/cgi/engine_details.cgi?match_length=30&print=Details&each_game=1&eng=Stockfish%2018%2064-bit%204CPU), a well-established independent rating list that shows Stockfish's strength scaling significantly from 1 to 4 threads with diminishing returns beyond that. 4 threads represents the sweet spot between analysis quality and resource consumption â€” strong enough to produce evaluations comparable to what chess.com and lichess use, without over-provisioning CPU in a containerized environment.

---

## Storage & Data

---

## Microservices Rebuild (v0.3.x)

### Why microservices?

The original monolith combined Stockfish, DuckDB, and JupyterLab in a single container. As analysis requirements grew - multiple concurrent positions, long-running engine jobs, independent scaling of the engine layer - the monolith became a constraint. The rebuild separates concerns cleanly: each service does one thing and can be scaled, deployed, and updated independently.

### engine-instance: one FEN at a time

Each engine instance processes a single position at a time. This is a deliberate design choice - Stockfish is CPU-bound and benefits from full resource allocation per analysis. The async job pattern (BackgroundTasks + module-level state + threading.Lock) allows the HTTP layer to remain responsive while the engine runs for minutes without blocking the event loop.

### engine-master: observer, not owner

The master holds no analysis state. It observes instance health, fans out requests in parallel via ThreadPoolExecutor, and aggregates results. Scaling is handled by patching the StatefulSet replica count via the Kubernetes API on startup and shutdown.

### StatefulSet for engine instances

Engine instances use a StatefulSet (not a Deployment) because the master addresses each pod individually via stable DNS. A Deployment would provide no stable pod identity. The headless service (clusterIP: None) enables per-pod DNS without load balancing, which is exactly what fan-out requires.

### Shared schemas package

All Pydantic models shared across services live in chess-reporter-schemas, a separate uv workspace member. This prevents schema drift between services and makes the contract between instance and master explicit and versioned.

### Port conventions

Internal ports follow a simple numeric convention: master=1000, instances=1001-1023 (mask 1999). This mirrors the logical hierarchy without wasting the NodePort range (30000-32767), which is reserved for external exposure only.

### PostgreSQL

PostgreSQL replaces DuckDB as the persistence layer for the microservices architecture. DuckDB remains suitable for local analytical exploration (JupyterLab), but PostgreSQL is the right choice for a multi-service system where multiple pods need concurrent read/write access. Connection is injected via DATABASE_URL environment variable, allowing transparent swap between local (docker-compose) and AWS RDS without code changes.

### Environment files by service and environment

Credentials are split into per-service, per-environment .env files (.env.postgresql.local, .env.k8s, etc.) rather than a single .env. This prevents credential leakage across services and makes the AWS migration path explicit: swap .env.postgresql.local for .env.postgresql.aws with the RDS endpoint.
