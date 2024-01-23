import random, string
import threading
import config
from benchmark import benchutils

COL_N = 10
COND_N = 10
zipf_gen = benchutils.ZipfGenerator(100, 0.99)

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def get_stmt_for_load(start_id, record_num, step):
    # prepare cols name
    col_names = ['ID']
    for i in range(COL_N):
        col_names.append("COL{}".format(i+1))
    col_names.append("lineage")
    # for i in range(COND_N):
    #     col_names.append("COND{}".format(i+1))

    # create bulk insert statement
    stmt = "INSERT INTO bt (" + ",".join(col_names) + ") VALUES "
    records = []
    for i in range(start_id, start_id + record_num * step, step):
        cols = []
        conds = []
        for _ in range(COL_N):
            cols.append("'"+str(randomname(10))+"'")
        # for _ in range(COND_N):
        #     conds.append(str(random.randint(0, 99)))
        # record = "(" + ",".join([str(i)] + cols + ["'"+config.peer_name+"-bt-"+str(i)+"'"] + conds) + ")"
        values = [str(i)] + cols + [f"'{config.peer_name}-bt-{i}'"]
        values = ",".join(values)
        record = f"({values})"
        records.append(record)
    stmt = stmt + ",".join(records)
    return stmt
