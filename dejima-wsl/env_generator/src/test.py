import random, string

COND_N = 10

def get_stmt_for_load(peer_num, start_id, record_num, step):
    # prepare cols name
    col_names = []
    if peer_num <= 5:
        col_names = ["V", "L", "D", "R", "P", "LINEAGE", "COND1", "COND2", "COND3", "COND4", "COND5", "COND6", "COND7", "COND8", "COND9", "COND10"]
    else:
        col_names = ["V", "L", "D", "R", "T", "AL1", "AL2", "AL3", "AL4", "AL5", "LINEAGE", "COND1", "COND2", "COND3", "COND4", "COND5", "COND6", "COND7", "COND8", "COND9", "COND10"]

    # create bulk insert statement
    stmt = "INSERT INTO mt (" + ",".join(col_names) + ") VALUES "
    if peer_num > 5:
        stmt = "INSERT INTO bt (" + ",".join(col_names) + ") VALUES "
    records = []
    for i in range(start_id, start_id + record_num * step, step):
        cols = []
        als = []
        conds = []
        
        cols.append(str(random.randint(1, 9999)))
        cols.append(str(random.randint(1, 9999)))
        cols.append(str(random.randint(0, 1)))
        if peer_num <= 5:
            cols.append("'"+str(random.choice(['A', 'B', 'C', 'D', 'E']))+"'")
        else:
            cols.append("'"+str(random.choice(string.ascii_lowercase))+"'")
            for _ in range(5):
                als.append(random.choice(['TRUE', 'FALSE']))
        for _ in range(COND_N):
            conds.append(str(random.randint(0, 99)))
            
        if peer_num <= 5:
            record = "(" + ",".join([str(i)] + cols + ["'"+"Peer"+"-mt-"+str(i)+"'"] + conds) + ")"
        else:
            record = "(" + ",".join([str(i)] + cols + als + ["'"+"Peer"+"-bt-"+str(i)+"'"] + conds) + ")"
        records.append(record)
        
    stmt = stmt + ",".join(records)
    print(stmt)
    
for i in range(1, 10+1):
    get_stmt_for_load(i, 1, 2, 10)