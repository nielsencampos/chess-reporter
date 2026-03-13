# DATA_DICTIONARY.md

Data dictionary for the Chess Reporter DuckDB database (`data/database/main.duckdb`).

---

## Schemas

| Schema | Description |
|--------|-------------|
| `chess_reporter` | Internal application tables — engine config and position evaluations |
| `workspace` | User sandbox for generated outputs, analysis queries, and ad-hoc exploration |

---

## Tables

### `chess_reporter.chess_engine`

Chess engine configuration data. Each row represents a unique engine setup used for analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `chess_engine_id` | TEXT | NOT NULL | Unique identifier (PK) |
| `name` | TEXT | NOT NULL | Name and version of the engine (e.g. `Stockfish 18`) |
| `threads` | BIGINT | NOT NULL | Number of threads configured (≥ 1) |
| `hash_table_mb` | BIGINT | NOT NULL | Hash table size in megabytes (≥ 1024) |
| `depth` | BIGINT | NOT NULL | Search depth (≥ 15) |
| `evaluation_runs` | BIGINT | NOT NULL | Number of sequential evaluation runs (≥ 3, must be odd) |
| `ingested_at` | TIMESTAMP | NOT NULL | When the record was ingested (default: `CURRENT_TIMESTAMP`) |

**Constraints:**
- `threads_valid` — `threads >= 1`
- `hash_table_mb_valid` — `hash_table_mb >= 1024`
- `depth_valid` — `depth >= 15`
- `evaluation_runs_valid` — `evaluation_runs >= 3 AND evaluation_runs % 2 = 1`

---

### `chess_reporter.position`

Aggregated evaluation results for a specific chess position. Each row is the statistical summary of N sequential engine runs.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `position_id` | TEXT | NOT NULL | Unique identifier (PK) |
| `chess_engine_id` | TEXT | NOT NULL | Engine used for the evaluation (FK → `chess_engine`) |
| `fen` | TEXT | NOT NULL | FEN string representing the position |
| `termination` | TEXT | NOT NULL | Termination status of the position (see values below) |
| `result` | TEXT | NOT NULL | Result of the game: `ongoing`, `white_won`, `black_won`, `draw` |
| `turn` | TEXT | NOT NULL | Player to move: `white` or `black` |
| `chess960` | BOOLEAN | NOT NULL | Whether the position originates from a Chess960 (Fischer Random) game |
| `board` | TEXT | NOT NULL | Board string representation of the position |
| `median_score_type` | TEXT | NOT NULL | Score type of the median (definitive) eval: `cp` or `mate` |
| `median_score_value` | BIGINT | NOT NULL | Score value of the median eval (centipawns or mate in N) |
| `minimum_score_type` | TEXT | NOT NULL | Score type of the minimum eval: `cp` or `mate` |
| `minimum_score_value` | BIGINT | NOT NULL | Score value of the minimum eval |
| `maximum_score_type` | TEXT | NOT NULL | Score type of the maximum eval: `cp` or `mate` |
| `maximum_score_value` | BIGINT | NOT NULL | Score value of the maximum eval |
| `median_depth` | BIGINT | NOT NULL | Median search depth across all runs |
| `median_seldepth` | BIGINT | NOT NULL | Median selective search depth across all runs |
| `median_time_in_seconds` | DOUBLE | NOT NULL | Median evaluation time in seconds |
| `minimum_depth` | BIGINT | NOT NULL | Minimum search depth across all runs |
| `minimum_seldepth` | BIGINT | NOT NULL | Minimum selective search depth across all runs |
| `minimum_time_in_seconds` | DOUBLE | NOT NULL | Minimum evaluation time in seconds |
| `maximum_depth` | BIGINT | NOT NULL | Maximum search depth across all runs |
| `maximum_seldepth` | BIGINT | NOT NULL | Maximum selective search depth across all runs |
| `maximum_time_in_seconds` | DOUBLE | NOT NULL | Maximum evaluation time in seconds |
| `started_analysis_at` | TIMESTAMP | NOT NULL | When the engine analysis started |
| `finished_analysis_at` | TIMESTAMP | NOT NULL | When the engine analysis finished |
| `ingested_at` | TIMESTAMP | NOT NULL | When the record was ingested (default: `CURRENT_TIMESTAMP`) |

**`termination` valid values:**

| Value | Description |
|-------|-------------|
| `ongoing` | Game still in progress |
| `checkmate` | Game ended by checkmate |
| `resignation` | Player resigned |
| `timeout` | Player lost on time |
| `abandonment` | Player abandoned the game |
| `variant` | Game ended by variant-specific rule |
| `draw_by_agreement` | Players agreed to a draw |
| `stalemate` | Draw by stalemate |
| `insufficient_material` | Draw by insufficient material |
| `threefold_repetition` | Draw by threefold repetition |
| `fifty_moves_rule` | Draw by fifty-move rule |
| `fivefold_repetition` | Draw by fivefold repetition |
| `seventyfive_moves` | Draw by 75-move rule |
| `timeout_draw_by_insufficient_material` | Timeout with insufficient material to checkmate |
| `variant_draw` | Draw by variant-specific rule |

**Foreign keys:**
- `chess_engine_id` → `chess_reporter.chess_engine.chess_engine_id`

---

### `chess_reporter.position_analysis`

Individual engine evaluation for a specific position — one row per run. Aggregated into `position`.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `position_analysis_id` | TEXT | NOT NULL | Unique identifier (PK) |
| `position_id` | TEXT | NOT NULL | Position being analyzed (FK → `position`) |
| `position_analysis_index` | BIGINT | NOT NULL | Run index (1-based, unique per position) |
| `score_type` | TEXT | NOT NULL | Score type: `cp` (centipawns) or `mate` (mate in N) |
| `score_value` | BIGINT | NOT NULL | Score value: centipawns or mate in N moves |
| `depth` | BIGINT | NOT NULL | Search depth for this run (≥ 0) |
| `seldepth` | BIGINT | NOT NULL | Selective search depth for this run (≥ 0) |
| `time_in_seconds` | DOUBLE | NOT NULL | Time taken for this run |
| `is_forced_result` | BOOLEAN | NOT NULL | `true` if the score comes from a forced game result, not engine evaluation |
| `started_analysis_at` | TIMESTAMP | NOT NULL | When this run started |
| `finished_analysis_at` | TIMESTAMP | NOT NULL | When this run finished (≥ `started_analysis_at`) |
| `ingested_at` | TIMESTAMP | NOT NULL | When the record was ingested (default: `CURRENT_TIMESTAMP`) |

**Constraints:**
- `UNIQUE(position_id, position_analysis_index)` — no duplicate run index per position
- `position_analysis_index_valid` — `position_analysis_index >= 1`
- `score_type_valid` — `score_type IN ('cp', 'mate')`
- `analysis_at_valid` — `finished_analysis_at >= started_analysis_at`

**Foreign keys:**
- `position_id` → `chess_reporter.position.position_id`

---

## Relationships

```
chess_engine ──< position ──< position_analysis
```

One engine configuration → many positions → many individual analysis runs per position.
