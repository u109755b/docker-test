DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d10_12 varchar,
    d12_13 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
