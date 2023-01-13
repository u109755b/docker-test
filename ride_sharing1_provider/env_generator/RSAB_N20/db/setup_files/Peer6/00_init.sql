DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d3_6 varchar,
    d6_9 varchar,
    d6_19 varchar,
    d6_20 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
