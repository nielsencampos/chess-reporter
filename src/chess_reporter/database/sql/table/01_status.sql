CREATE TABLE IF NOT EXISTS chess_reporter.status (
    id          TEXT NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name),
    UNIQUE (description)
);
COMMENT ON TABLE chess_reporter.status
    IS 'Status reference table';
COMMENT ON COLUMN chess_reporter.status.id
    IS 'Identifier of the status';
COMMENT ON COLUMN chess_reporter.status.name
    IS 'Name of the status';
COMMENT ON COLUMN chess_reporter.status.description
    IS 'Description of the status';
COMMENT ON COLUMN chess_reporter.status.created_at
    IS 'Timestamp of the creation of the status';
COMMENT ON COLUMN chess_reporter.status.updated_at
    IS 'Timestamp of the last update';

MERGE INTO chess_reporter.status AS t
USING (
    SELECT
        'pending' AS id,
        'Pending' AS name,
        'Processing has not started yet (in queue)' AS description
    UNION ALL
    SELECT
        'in_progress' AS id,
        'In progress' AS name,
        'Currently being processed' AS description
    UNION ALL
    SELECT
        'completed' AS id,
        'Completed' AS name,
        'Processing finished successfully' AS description
    UNION ALL
    SELECT
        'failed' AS id,
        'Failed' AS name,
        'Processing failed' AS description
) AS s
ON t.id = s.id
WHEN NOT MATCHED THEN
    INSERT (id, name, description)
    VALUES (s.id, s.name, s.description)
WHEN MATCHED AND (t.name <> s.name OR t.description <> s.description) THEN
    UPDATE SET
        name = s.name,
        description = s.description,
        updated_at = CURRENT_TIMESTAMP;
