DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d4_15 varchar,
    d15_17 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
