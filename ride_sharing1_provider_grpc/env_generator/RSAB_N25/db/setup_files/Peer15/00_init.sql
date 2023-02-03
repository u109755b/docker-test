DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d7_15 varchar,
    d15_16 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
