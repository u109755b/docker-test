DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d6_7 varchar,
    d7_8 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
