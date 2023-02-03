DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_2 varchar,
    d2_4 varchar,
    d2_6 varchar,
    d2_7 varchar,
    d2_9 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
