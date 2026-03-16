CREATE TABLE IF NOT EXISTS chess_reporter.engine_config (
    id            TEXT NOT NULL PRIMARY KEY,
    name_version  TEXT NOT NULL,
    threads       BIGINT NOT NULL,
    hash_table_mb BIGINT NOT NULL,
    depth         BIGINT NOT NULL,
    multipv       BIGINT NOT NULL,
    analyses      BIGINT NOT NULL,
    parallelism   BOOLEAN NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status        TEXT NOT NULL DEFAULT 'completed',
    UNIQUE (name_version, threads, hash_table_mb, depth, multipv, analyses, parallelism),
    CONSTRAINT threads_valid CHECK (threads >= 1),
    CONSTRAINT hash_table_mb_valid CHECK (hash_table_mb >= 64),
    CONSTRAINT depth_valid CHECK (depth >= 15),
    CONSTRAINT multipv_valid CHECK (multipv >= 3),
    CONSTRAINT analyses_valid CHECK (analyses >= 3 AND analyses % 2 = 1),
    FOREIGN KEY (status) REFERENCES chess_reporter.status (id)
);
COMMENT ON TABLE chess_reporter.engine_config
    IS 'Engine configuration data';
COMMENT ON COLUMN chess_reporter.engine_config.id
    IS 'Unique identifier of engine configuration (PK)';
COMMENT ON COLUMN chess_reporter.engine_config.name_version
    IS 'Name and version of the engine';
COMMENT ON COLUMN chess_reporter.engine_config.threads
    IS 'Number of threads configured';
COMMENT ON COLUMN chess_reporter.engine_config.hash_table_mb
    IS 'Size of the hash table in megabytes';
COMMENT ON COLUMN chess_reporter.engine_config.depth
    IS 'Search depth';
COMMENT ON COLUMN chess_reporter.engine_config.multipv
    IS 'Number of principal variations to calculate';
COMMENT ON COLUMN chess_reporter.engine_config.analyses
    IS 'Number of analyses to perform';
COMMENT ON COLUMN chess_reporter.engine_config.parallelism
    IS 'Whether to enable parallelism for the analyses or run in series';
COMMENT ON COLUMN chess_reporter.engine_config.created_at
    IS 'Timestamp of the creation of the engine configuration';
COMMENT ON COLUMN chess_reporter.engine_config.updated_at
    IS 'Timestamp of the last update of the engine configuration';
COMMENT ON COLUMN chess_reporter.engine_config.status
    IS 'Status of the engine configuration';
