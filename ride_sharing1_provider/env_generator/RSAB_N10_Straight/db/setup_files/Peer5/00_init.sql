DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d4_5 varchar,
    d5_6 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
