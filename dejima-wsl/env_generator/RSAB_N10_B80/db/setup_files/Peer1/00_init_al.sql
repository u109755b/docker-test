DROP TABLE IF EXISTS MT;
CREATE TABLE MT (
	V	    serial primary key,
	L	    int NOT NULL,
	D	    int NOT NULL,
	R	    int NOT NULL,
	P	    varchar NOT NULL,
	LINEAGE	varchar NOT NULL,
	COND1	int NOT NULL,
	COND2	int NOT NULL,
	COND3	int NOT NULL,
	COND4	int NOT NULL,
	COND5	int NOT NULL,
	COND6	int NOT NULL,
	COND7	int NOT NULL,
	COND8	int NOT NULL,
	COND9	int NOT NULL,
	COND10	int NOT NULL
);

CREATE INDEX ON mt (lineage);