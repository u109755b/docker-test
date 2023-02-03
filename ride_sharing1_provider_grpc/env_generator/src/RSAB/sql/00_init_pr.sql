DROP TABLE IF EXISTS BT;
CREATE TABLE BT (
	V	    serial primary key,
	L	    int NOT NULL,
	D	    int NOT NULL,
	R	    int NOT NULL,
	T	    varchar NOT NULL,
	AL1	    boolean NOT NULL,
	AL2	    boolean NOT NULL,
	AL3	    boolean NOT NULL,
	AL4	    boolean NOT NULL,
	AL5	    boolean NOT NULL,
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

CREATE INDEX ON bt (lineage);