DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d7_10 varchar,
    d10_19 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
