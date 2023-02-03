DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_3 varchar,
    d3_5 varchar,
    d3_11 varchar,
    d3_17 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
