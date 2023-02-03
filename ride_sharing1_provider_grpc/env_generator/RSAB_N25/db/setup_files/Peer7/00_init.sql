DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d2_7 varchar,
    d7_8 varchar,
    d7_10 varchar,
    d7_15 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
