DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    AL5 varchar,
    AL9 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
