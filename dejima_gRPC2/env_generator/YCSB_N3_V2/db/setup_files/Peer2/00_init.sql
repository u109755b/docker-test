CREATE TABLE BT (
	ID	serial primary key,
	COL1	varchar,
	COL2	varchar,
	COL3	varchar,
	COL4	varchar,
	COL5	varchar,
	COL6	varchar,
	COL7	varchar,
	COL8	varchar,
	COL9	varchar,
	COL10	varchar,
	LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
