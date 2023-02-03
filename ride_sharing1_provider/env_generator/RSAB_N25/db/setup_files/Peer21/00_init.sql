DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d19_21 varchar,
    d21_23 varchar,
    d21_24 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
