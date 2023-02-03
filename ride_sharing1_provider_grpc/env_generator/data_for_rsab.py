init_sql = """\
DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V serial primary key,
    L int,
    D int,
    R int,
columns
    LINEAGE	varchar
);

CREATE INDEX ON bt (lineage);
"""

birds_datalog = """\
% schema:
source bt('V':int, 'L':int, 'D':int, 'R':int, columns, 'LINEAGE':string).
view dt_name('V':int, 'L':int, 'D':int, 'R':int, 'LINEAGE':string).

% view definition
dt_name(V,L,D,R,LINEAGE) :- bt(V,L,D,R,underscores_dt,LINEAGE), dt_flag.

% rules for update strategy:
-bt(V,L,D,R,dt_names,LINEAGE) :- bt(V,L,D,R,dt_names,LINEAGE), NOT dt_name(V,L,D,R,LINEAGE), dt_flag.
+bt(V,L,D,R,dt_names,LINEAGE) :- NOT bt(V,L,D,R,underscores,LINEAGE), dt_name(V,L,D,R,LINEAGE), bt(V,_,_,_,dt_names_under,_), dt_flag.
+bt(V,L,D,R,dt_names,LINEAGE) :- NOT bt(V,L,D,R,underscores,LINEAGE), dt_name(V,L,D,R,LINEAGE), NOT bt(V,_,_,_,underscores,_), all_flags.
"""