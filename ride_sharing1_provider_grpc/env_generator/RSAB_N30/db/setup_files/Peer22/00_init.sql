DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
    d20_22 varchar,
    d22_23 varchar,
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
