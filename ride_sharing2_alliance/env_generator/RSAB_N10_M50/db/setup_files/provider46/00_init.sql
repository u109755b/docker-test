DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL1 varchar,
    AL4 varchar,
    AL7 varchar,
    AL5 varchar,
    AL2 varchar,
    AL3 varchar,
    AL8 varchar,
    AL10 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
