DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d7_8 varchar,
    d8_9 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
