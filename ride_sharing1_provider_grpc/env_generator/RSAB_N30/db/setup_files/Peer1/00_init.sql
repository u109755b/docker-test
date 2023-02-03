DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_2 varchar,
    d1_5 varchar,
    d1_7 varchar,
    d1_8 varchar,
    d1_9 varchar,
    d1_10 varchar,
    d1_11 varchar,
    d1_13 varchar,
    d1_19 varchar,
    d1_28 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
