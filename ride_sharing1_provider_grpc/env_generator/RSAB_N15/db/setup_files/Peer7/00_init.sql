DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_7 varchar,
    d7_11 varchar,
    d7_14 varchar,
    d7_15 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
