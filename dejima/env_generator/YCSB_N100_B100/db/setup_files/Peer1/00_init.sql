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
	LINEAGE	varchar,
	COND1	int,
	COND2	int,
	COND3	int,
	COND4	int,
	COND5	int,
	COND6	int,
	COND7	int,
	COND8	int,
	COND9	int,
	COND10	int
);

CREATE INDEX ON bt (lineage);
