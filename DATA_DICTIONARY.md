# DATA_DICTIONARY.md

Data dictionary for the Chess Reporter DuckDB database (`data/database/main.duckdb`).

---

## Schemas

| Schema | Description |
|--------|-------------|
| `chess_reporter` | Internal application tables — status reference and engine configuration |
| `workspace` | User sandbox for generated outputs, analysis queries, and ad-hoc exploration |

---

## Tables

### `chess_reporter.status`

Status reference table. Seeded on startup by `DatabaseBootstrapper`. Each row represents a lifecycle state used as a foreign key in other tables.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | TEXT | NOT NULL | Identifier of the status (PK) |
| `name` | TEXT | NOT NULL | Human-readable name |
| `description` | TEXT | NOT NULL | Description of the status |
| `created_at` | TIMESTAMP | NOT NULL | When the record was created (default: `CURRENT_TIMESTAMP`) |
| `updated_at` | TIMESTAMP | NOT NULL | When the record was last updated (default: `CURRENT_TIMESTAMP`) |

**Constraints:**
- `UNIQUE(name)`
- `UNIQUE(description)`

**Seeded values:**

| `id` | `name` | `description` |
|------|--------|---------------|
| `pending` | Pending | Processing has not started yet (in queue) |
| `in_progress` | In progress | Currently being processed |
| `completed` | Completed | Processing finished successfully |
| `failed` | Failed | Processing failed |

---

### `chess_reporter.engine_config`

Engine configuration data. Each row represents a unique combination of engine settings used for analysis. Created on first use by `EngineManager`.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | TEXT | NOT NULL | Unique identifier (PK) — SHA-512 hash of all config fields |
| `name_version` | TEXT | NOT NULL | Name and version of the engine (e.g. `Stockfish 18`) |
| `threads` | BIGINT | NOT NULL | Number of threads configured (≥ 1) |
| `hash_table_mb` | BIGINT | NOT NULL | Hash table size in megabytes (≥ 64) |
| `depth` | BIGINT | NOT NULL | Search depth (≥ 15) |
| `multipv` | BIGINT | NOT NULL | Number of principal variations to calculate (≥ 3) |
| `analyses` | BIGINT | NOT NULL | Number of analysis runs (≥ 3, must be odd) |
| `parallelism` | BOOLEAN | NOT NULL | Whether analyses run in parallel (`true`) or series (`false`) |
| `created_at` | TIMESTAMP | NOT NULL | When the record was created (default: `CURRENT_TIMESTAMP`) |
| `updated_at` | TIMESTAMP | NOT NULL | When the record was last updated (default: `CURRENT_TIMESTAMP`) |
| `status` | TEXT | NOT NULL | Lifecycle status (FK → `chess_reporter.status`) |

**Constraints:**
- `UNIQUE(name_version, threads, hash_table_mb, depth, multipv, analyses, parallelism)`
- `threads_valid` — `threads >= 1`
- `hash_table_mb_valid` — `hash_table_mb >= 64`
- `depth_valid` — `depth >= 15`
- `multipv_valid` — `multipv >= 3`
- `analyses_valid` — `analyses >= 3 AND analyses % 2 = 1`

**Foreign keys:**
- `status` → `chess_reporter.status.id`

---

## Relationships

```
status ──< engine_config
```

One status value → many engine configuration records.
