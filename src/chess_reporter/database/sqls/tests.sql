-- =================================================================================================
-- Tests for DuckDB
-- =================================================================================================
CREATE OR REPLACE TABLE test.dummy (
    dummy_id   BIGINT NOT NULL PRIMARY KEY,
    dummy_name TEXT NOT NULL
);

INSERT INTO test.dummy (dummy_id, dummy_name) VALUES (
    (0, 'Zero'), (1, 'One'), (2, 'Two'), (3, 'Three'), (4, 'Four'), (5, 'Five'), (6, 'Six'),
    (7, 'Seven'), (8, 'Eight'), (9, 'Nine')
);

DELETE FROM test.dummy WHERE dummy_id > 7;

UPDATE test.dummy SET dummy_id = 10, dummy_name = 'Ten' WHERE dummy_id = 1;

DROP TABLE IF EXISTS test.dummy;
