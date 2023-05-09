DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL6 varchar,
    AL1 varchar,
    AL3 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
