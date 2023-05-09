DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL9 varchar,
    AL5 varchar,
    AL1 varchar,
    AL2 varchar,
    AL6 varchar,
    AL10 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
