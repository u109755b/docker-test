init_sql_alliance = """\
DROP TABLE IF EXISTS mt;
CREATE TABLE mt(
    V serial primary key,
    L int,
    D int,
    R int,
    P int,
    LINEAGE	varchar
);

CREATE INDEX ON mt (lineage);
"""

init_sql_provider = """\
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


birds_datalog_alliance = """\
% schema:
source mt('V':int, 'L':int, 'D':int, 'R':int, 'P':int, 'LINEAGE':string).
view dt_name('V':int, 'L':int, 'D':int, 'R':int, 'LINEAGE':string).

% view definition
dt_name(V,L,D,R,LINEAGE) :- mt(V,L,D,R,P,LINEAGE), p_flag.

% rules for update strategy:
-mt(V,L,D,R,P,LINEAGE) :- mt(V,L,D,R,P,LINEAGE), NOT dt_name(V,L,D,R,LINEAGE), p_flag.
+mt(V,L,D,R,P,LINEAGE) :- NOT mt(V,L,D,R,P,LINEAGE), dt_name(V,L,D,R,LINEAGE), p_flag.
"""

birds_datalog_provider = """\
% schema:
source bt('V':int, 'L':int, 'D':int, 'R':int, columns, 'LINEAGE':string).
view dt_name('V':int, 'L':int, 'D':int, 'R':int, 'LINEAGE':string).

% view definition
dt_name(V,L,D,R,LINEAGE) :- bt(V,L,D,R,underscores_alliance,LINEAGE), alliance_flag.

% rules for update strategy:
-bt(V,L,D,R,alliances,LINEAGE) :- bt(V,L,D,R,alliances,LINEAGE), NOT dt_name(V,L,D,R,LINEAGE), alliance_flag.
+bt(V,L,D,R,alliances,LINEAGE) :- NOT bt(V,L,D,R,underscores,LINEAGE), dt_name(V,L,D,R,LINEAGE), bt(V,_,_,_,alliances_under,_), alliance_flag.
+bt(V,L,D,R,alliances,LINEAGE) :- NOT bt(V,L,D,R,underscores,LINEAGE), dt_name(V,L,D,R,LINEAGE), NOT bt(V,_,_,_,underscores,_), all_flags.
"""