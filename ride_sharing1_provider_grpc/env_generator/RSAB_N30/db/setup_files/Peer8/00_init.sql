DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_8 varchar,
    d8_20 varchar,
    d8_24 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
