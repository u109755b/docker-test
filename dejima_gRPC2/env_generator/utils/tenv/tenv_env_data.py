# bt
# columns
columns = {
    "ID":	    "int",
	"COL":	    "string",
	"LINEAGE":	"string",
}

# column_definitions
column_definitions = [f"'{key}': {value}" for key, value in columns.items()]
column_definitions = ", \n\t".join(column_definitions)
column_definitions = f"\n\t{column_definitions}\n"

# column_names
column_names = ", ".join([s.upper() for s in columns.keys()])

datalog_dt = f"""\
% schema
source bt({column_definitions}).
view dt_name({column_definitions}).

% view definition
dt_name({column_names}) :- bt({column_names}).

% rules for update strategy
-bt({column_names}) :- bt({column_names}), NOT dt_name({column_names}).
+bt({column_names}) :- NOT bt({column_names}), dt_name({column_names}).
"""