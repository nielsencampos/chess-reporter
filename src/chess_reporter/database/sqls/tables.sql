-- =================================================================================================
-- Chess Reporter Database Tables (Only internal application tables [chess_reporter])
-- =================================================================================================
-- chess_engine      : Chess engine configuration data
-- position          : Aggregated evaluation results for specific chess positions
-- position_analysis : Single evaluation results for specific chess positions
-- =================================================================================================
CREATE TABLE IF NOT EXISTS chess_reporter.chess_engine (
    chess_engine_id TEXT NOT NULL PRIMARY KEY,
    name            TEXT NOT NULL,
    threads         BIGINT NOT NULL,
    hash_table_mb   BIGINT NOT NULL,
    depth           BIGINT NOT NULL,
    evaluation_runs BIGINT NOT NULL,
    ingested_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, threads, hash_table_mb, depth, evaluation_runs),
    CONSTRAINT threads_valid CHECK (threads >= 1),
    CONSTRAINT hash_table_mb_valid CHECK (hash_table_mb >= 1024),
    CONSTRAINT depth_valid CHECK (depth >= 15),
    CONSTRAINT evaluation_runs_valid CHECK (evaluation_runs >= 3 AND evaluation_runs % 2 = 1)
);
COMMENT ON TABLE chess_reporter.chess_engine
    IS 'Chess engine configuration data';
COMMENT ON COLUMN chess_reporter.chess_engine.chess_engine_id
    IS 'Unique identifier of chess engine (PK)';
COMMENT ON COLUMN chess_reporter.chess_engine.name
    IS 'Name and version of chess engine';
COMMENT ON COLUMN chess_reporter.chess_engine.threads
    IS 'Number of threads configured';
COMMENT ON COLUMN chess_reporter.chess_engine.hash_table_mb
    IS 'Size of the hash table in megabytes';
COMMENT ON COLUMN chess_reporter.chess_engine.depth
    IS 'Search depth';
COMMENT ON COLUMN chess_reporter.chess_engine.evaluation_runs
    IS 'Number of evaluation runs to perform';
COMMENT ON COLUMN chess_reporter.chess_engine.ingested_at
    IS 'Internal timestamp to set when the data was ingested';

CREATE TABLE IF NOT EXISTS chess_reporter.position (
    position_id             TEXT NOT NULL PRIMARY KEY,
    chess_engine_id         TEXT NOT NULL,
    fen                     TEXT NOT NULL,
    termination             TEXT NOT NULL,
    result                  TEXT NOT NULL,
    turn                    TEXT NOT NULL,
    chess960                BOOLEAN NOT NULL,
    board                   TEXT NOT NULL,
    median_score_type       TEXT NOT NULL,
    median_score_value      BIGINT NOT NULL,
    minimum_score_type      TEXT NOT NULL,
    minimum_score_value     BIGINT NOT NULL,
    maximum_score_type      TEXT NOT NULL,
    maximum_score_value     BIGINT NOT NULL,
    median_depth            BIGINT NOT NULL,
    median_seldepth         BIGINT NOT NULL,
    median_time_in_seconds  DOUBLE PRECISION NOT NULL,
    minimum_depth           BIGINT NOT NULL,
    minimum_seldepth        BIGINT NOT NULL,
    minimum_time_in_seconds DOUBLE PRECISION NOT NULL,
    maximum_depth           BIGINT NOT NULL,
    maximum_seldepth        BIGINT NOT NULL,
    maximum_time_in_seconds DOUBLE PRECISION NOT NULL,
    started_analysis_at     TIMESTAMP NOT NULL,
    finished_analysis_at    TIMESTAMP NOT NULL,
    ingested_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chess_engine_id, fen, termination, result),
    CONSTRAINT termination_valid CHECK (termination IN (
        'ongoing',
        'abandonment', 'checkmate', 'resignation', 'timeout', 'variant',
        'draw_by_agreement', 'timeout_draw_by_insufficient_material', 'stalemate',
        'insufficient_material', 'threefold_repetition', 'fifty_moves_rule', 'fivefold_repetition',
        'seventyfive_moves', 'variant_draw')),
    CONSTRAINT result_valid CHECK (result IN ('ongoing', 'white_won', 'black_won', 'draw')),
    CONSTRAINT turn_valid CHECK (turn IN ('white', 'black')),
    CONSTRAINT median_score_type_valid CHECK (median_score_type IN ('cp', 'mate')),
    CONSTRAINT minimum_score_type_valid CHECK (minimum_score_type IN ('cp', 'mate')),
    CONSTRAINT maximum_score_type_valid CHECK (maximum_score_type IN ('cp', 'mate')),
    FOREIGN KEY (chess_engine_id) REFERENCES chess_reporter.chess_engine (chess_engine_id)
);
COMMENT ON TABLE chess_reporter.position
    IS 'Aggregated evaluation results for specific chess positions';
COMMENT ON COLUMN chess_reporter.position.position_id
    IS 'Unique identifier of chess position (PK)';
COMMENT ON COLUMN chess_reporter.position.chess_engine_id
    IS 'Identifier of the chess engine used for the evaluation (FK)';
COMMENT ON COLUMN chess_reporter.position.fen
    IS 'FEN string representing the chess position';
COMMENT ON COLUMN chess_reporter.position.termination
    IS 'Termination status of the position evaluation';
COMMENT ON COLUMN chess_reporter.position.result
    IS 'Result of the position evaluation';
COMMENT ON COLUMN chess_reporter.position.turn
    IS 'Player to move: `white` or `black`';
COMMENT ON COLUMN chess_reporter.position.chess960
    IS 'Flag indicating the position originates from a Chess960 (Fischer Random) game';
COMMENT ON COLUMN chess_reporter.position.board
    IS 'Board string representation of the chess position';
COMMENT ON COLUMN chess_reporter.position.median_score_type
    IS 'Type of the median and final score: `cp` for centipawns or `mate` for mate in N moves';
COMMENT ON COLUMN chess_reporter.position.median_score_value
    IS 'Value of the median and final score: centipawns or mate in N moves';
COMMENT ON COLUMN chess_reporter.position.minimum_score_type
    IS 'Type of the minimum score: `cp` for centipawns or `mate` for mate in N moves';
COMMENT ON COLUMN chess_reporter.position.minimum_score_value
    IS 'Value of the minimum score: centipawns or mate in N moves';
COMMENT ON COLUMN chess_reporter.position.maximum_score_type
    IS 'Type of the maximum score: `cp` for centipawns or `mate` for mate in N moves';
COMMENT ON COLUMN chess_reporter.position.maximum_score_value
    IS 'Value of the maximum score: centipawns or mate in N moves';
COMMENT ON COLUMN chess_reporter.position.median_depth
    IS 'Median search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.median_seldepth
    IS 'Median selective search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.median_time_in_seconds
    IS 'Median time taken in seconds across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.minimum_depth
    IS 'Minimum search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.minimum_seldepth
    IS 'Minimum selective search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.minimum_time_in_seconds
    IS 'Minimum time taken in seconds across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.maximum_depth
    IS 'Maximum search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.maximum_seldepth
    IS 'Maximum selective search depth across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.maximum_time_in_seconds
    IS 'Maximum time taken in seconds across all evaluations for the position';
COMMENT ON COLUMN chess_reporter.position.started_analysis_at
    IS 'Timestamp indicating when the chess engine analysis for this position started';
COMMENT ON COLUMN chess_reporter.position.finished_analysis_at
    IS 'Timestamp indicating when the chess engine analysis for this position finished';
COMMENT ON COLUMN chess_reporter.position.ingested_at
    IS 'Internal timestamp to set when the data was ingested';

CREATE TABLE IF NOT EXISTS chess_reporter.position_analysis (
    position_analysis_id    TEXT NOT NULL PRIMARY KEY,
    position_id             TEXT NOT NULL,
    position_analysis_index BIGINT NOT NULL,
    score_type              TEXT NOT NULL,
    score_value             BIGINT NOT NULL,
    depth                   BIGINT NOT NULL,
    seldepth                BIGINT NOT NULL,
    time_in_seconds         DOUBLE PRECISION NOT NULL,
    is_forced_result        BOOLEAN NOT NULL,
    started_analysis_at     TIMESTAMP NOT NULL,
    finished_analysis_at    TIMESTAMP NOT NULL,
    ingested_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(position_id, position_analysis_index),
    CONSTRAINT position_analysis_index_valid CHECK (position_analysis_index >= 1),
    CONSTRAINT score_type_valid CHECK (score_type IN ('cp', 'mate')),
    CONSTRAINT depth_valid CHECK (depth >= 0),
    CONSTRAINT seldepth_valid CHECK (seldepth >= 0),
    CONSTRAINT analysis_at_valid CHECK (finished_analysis_at >= started_analysis_at),
    FOREIGN KEY (position_id) REFERENCES chess_reporter.position (position_id)
);
COMMENT ON TABLE chess_reporter.position_analysis
    IS 'Single evaluation results for specific chess positions';
COMMENT ON COLUMN chess_reporter.position_analysis.position_analysis_id
    IS 'Unique identifier of position analysis (PK)';
COMMENT ON COLUMN chess_reporter.position_analysis.position_id
    IS 'Identifier of the chess position being analyzed (FK)';
COMMENT ON COLUMN chess_reporter.position_analysis.position_analysis_index
    IS 'Index of the analysis for the position';
COMMENT ON COLUMN chess_reporter.position_analysis.score_type
    IS 'Type of the score: `cp` for centipawns or `mate` for mate in N moves';
COMMENT ON COLUMN chess_reporter.position_analysis.score_value
    IS 'Value of the score: centipawns or mate in N moves';
COMMENT ON COLUMN chess_reporter.position_analysis.depth
    IS 'Search depth at which the chess engine evaluation was performed';
COMMENT ON COLUMN chess_reporter.position_analysis.seldepth
    IS 'Selective search depth at which the chess engine evaluation was performed';
COMMENT ON COLUMN chess_reporter.position_analysis.time_in_seconds
    IS 'Time taken in seconds for the chess engine to perform the evaluation';
COMMENT ON COLUMN chess_reporter.position_analysis.is_forced_result
    IS 'Indicates if the score is derived from a forced game result (no engine evaluation)';
COMMENT ON COLUMN chess_reporter.position_analysis.started_analysis_at
    IS 'Timestamp indicating when the chess engine analysis for this position started';
COMMENT ON COLUMN chess_reporter.position_analysis.finished_analysis_at
    IS 'Timestamp indicating when the chess engine analysis for this position finished';
COMMENT ON COLUMN chess_reporter.position_analysis.ingested_at
    IS 'Internal timestamp to set when the data was ingested';
