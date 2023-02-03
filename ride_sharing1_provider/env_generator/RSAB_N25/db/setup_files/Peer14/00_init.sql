DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d5_14 varchar,
    d14_18 varchar,
    d14_20 varchar,
    d14_25 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
