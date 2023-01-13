DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d8_9 varchar,
    d9_10 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
