DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL9 varchar,
    AL2 varchar,
    AL8 varchar,
    AL7 varchar,
    AL3 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
