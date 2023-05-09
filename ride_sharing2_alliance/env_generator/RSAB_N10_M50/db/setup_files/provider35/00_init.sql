DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL5 varchar,
    AL2 varchar,
    AL6 varchar,
    AL9 varchar,
    AL1 varchar,
    AL7 varchar,
    AL8 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
