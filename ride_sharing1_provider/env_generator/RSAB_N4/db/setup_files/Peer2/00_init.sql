DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_2 varchar,
    d2_3 varchar,
    d2_4 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
