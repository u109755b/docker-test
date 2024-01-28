CREATE TABLE BT (
	ID	serial primary key,
	COL	varchar,
	LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
