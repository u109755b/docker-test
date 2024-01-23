# customer
# columns
columns = {
    "c_w_id":           "int",
    "c_d_id":           "int",
    "c_id":             "int",
    "c_discount":       "string",
    "c_credit":         "string",
    "c_last":           "string",
    "c_first":          "string",
    "c_credit_lim":     "string",
    "c_balance":        "string",
    "c_ytd_payment":    "string",
    "c_payment_cnt":    "int",
    "c_delivery_cnt":   "int",
    "c_street_1":       "string",
    "c_street_2":       "string",
    "c_city":           "string",
    "c_state":          "string",
    "c_zip":            "string",
    "c_phone":          "string",
    "c_since":          "string",
    "c_middle":         "string",
    "c_data":           "string",
    "c_lineage":        "string",
}

# column_definitions
column_definitions = [f"'{key}': {value}" for key, value in columns.items()]
column_definitions = ", \n\t".join(column_definitions)
column_definitions = f"\n\t{column_definitions}\n"

# column_names
column_names = ", ".join([s.upper() for s in columns.keys()])

datalog_customer = f"""\
% schema
source customer({column_definitions}).
view dt_name({column_definitions}).

% view definition
dt_name({column_names}) :- customer({column_names}).

% rules for update strategy
-customer({column_names}) :- customer({column_names}), NOT dt_name({column_names}).
+customer({column_names}) :- NOT customer({column_names}), dt_name({column_names}).
"""



# stock
# columns
columns = {
    "s_w_id":       "int",
    "s_i_id":       "int",
    "s_quantity":   "string",
    "s_ytd":        "string",
    "s_order_cnt":  "int",
    "s_remote_cnt": "int",
    "s_data":       "string",
    "s_dist_01":    "string",
    "s_dist_02":    "string",
    "s_dist_03":    "string",
    "s_dist_04":    "string",
    "s_dist_05":    "string",
    "s_dist_06":    "string",
    "s_dist_07":    "string",
    "s_dist_08":    "string",
    "s_dist_09":    "string",
    "s_dist_10":    "string",
    "lineage":      "string",
}

# column_definitions
column_definitions = [f"'{key}': {value}" for key, value in columns.items()]
column_definitions = ", \n\t".join(column_definitions)
column_definitions = f"\n{column_definitions}\n"

# column_names
column_names = ", ".join([s.upper() for s in columns.keys()])

# datalog_stock
datalog_stock = f"""\
% schema
source stock({column_definitions}).
view dt_name({column_definitions}).

% view definition
dt_name({column_names}) :- stock({column_names}).

% rules for update strategy
-stock({column_names}) :- stock({column_names}), NOT dt_name({column_names}).
+stock({column_names}) :- NOT stock({column_names}), dt_name({column_names}).
"""
