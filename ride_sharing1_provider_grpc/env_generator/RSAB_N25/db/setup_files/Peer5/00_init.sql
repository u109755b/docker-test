DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d3_5 varchar,
    d5_14 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
