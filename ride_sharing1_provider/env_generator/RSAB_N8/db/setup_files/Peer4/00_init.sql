DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d1_4 varchar,
    d4_5 varchar,
    d4_6 varchar,
    d4_7 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
