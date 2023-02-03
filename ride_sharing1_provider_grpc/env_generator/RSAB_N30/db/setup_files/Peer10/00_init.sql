DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_10 varchar,
    d10_17 varchar,
    d10_27 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
