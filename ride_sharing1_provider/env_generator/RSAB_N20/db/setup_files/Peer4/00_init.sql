DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d2_4 varchar,
    d4_15 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
