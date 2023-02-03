DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d7_8 varchar,
    d8_12 varchar,
    d8_14 varchar,
    d8_16 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
