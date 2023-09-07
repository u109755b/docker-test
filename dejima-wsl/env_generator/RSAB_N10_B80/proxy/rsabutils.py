import random, string
import config
import threading

COL_N = 10
COND_N = 10

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

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
            record = "(" + ",".join([str(i)] + cols + ["'"+config.peer_name+"-mt-"+str(i)+"'"] + conds) + ")"
        else:
            record = "(" + ",".join([str(i)] + cols + als + ["'"+config.peer_name+"-bt-"+str(i)+"'"] + conds) + ")"
        records.append(record)
        
    stmt = stmt + ",".join(records)
    return stmt

def get_workload_for_rsab(read_num=5, write_num=5):
    stmts = []
    # Read
    for i in range(read_num):
        target_col = 'col{}'.format(random.randint(1,COL_N))
        stmts.append("SELECT {} FROM bt WHERE id={}".format(target_col, next(zipf_gen)))
    # Write
    for i in range(write_num):
        target_col = 'col{}'.format(random.randint(1,COL_N))
        stmts.append("UPDATE bt SET {}='{}' WHERE id={}".format(target_col, randomname(10), next(zipf_gen)))
    return stmts

# prepare zipf generator
class zipfGenerator:
    def __init__(self, n, theta):
        self.n = n
        self.theta = theta
        self.alpha = 1 / (1-theta)
        self.zetan = self.zeta(n, theta)
        self.eta = (1 - pow(2.0/n, 1-theta)) / (1 - self.zeta(2, theta) / self.zetan)
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            u = random.random()
            uz = u * self.zetan
            if uz < 1:
                return 1
            elif uz < 1 + pow(0.5, self.theta):
                return 2
            else:
                return 1 + int(self.n * pow(self.eta * u - self.eta + 1, self.alpha))

    def zeta(self, n, theta):
        sum = 0
        for i in range(1,n+1):
            sum += 1 / pow(i, theta)
        return sum