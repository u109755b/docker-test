import random, string
import config
import threading

COL_N = 10
COND_N = 10

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def get_stmt_for_load(start_id, record_num, step, max_hop):
    # prepare cols name
    col_names = ["V", "L", "D", "R"] + config.sorted_dt_list + ["LINEAGE"]

    # create bulk insert statement
    stmt = "INSERT INTO bt (" + ",".join(col_names) + ") VALUES "
    records = []
    for i in range(start_id, start_id + record_num * step, step):
        cols = []
        
        cols.append(str(random.randint(1, 9999)))
        cols.append(str(random.randint(1, 9999)))
        cols.append("0")
        for j in range(len(config.sorted_dt_list)):
            if max_hop == 0:
                cols.append("'false'")
            else:
                cols.append("'true'")
        
        record = "(" + ",".join([str(i)] + cols + ["'"+config.peer_name+"-bt-"+str(i)+"'"]) + ")"
        records.append(record)
        config.candidate_record_id_list.append(i)
        
    stmt = stmt + ",".join(records)
    return stmt


def get_workload_for_rsab():
    stmts = []
    
    L = random.randint(1, 9999)
    V_idx = random.randint(1, len(config.candidate_record_id_list))-1
    V = config.candidate_record_id_list[V_idx]
    # print(f"a = {config.candidate_record_id_list}, a[{V_idx}] = {V}")
    
    # print("created!")
    # for i in range(10):
    #     stmts.append("UPDATE bt SET L={}, R=0 WHERE V={}".format(L, V))
    
    r = random.randint(1, 100)
    if 0 < r and r <= 70:
        for i in range(5):
            L = random.randint(1, 9999)
            V_idx = random.randint(1, len(config.candidate_record_id_list))-1
            V = config.candidate_record_id_list[V_idx]
            stmts.append("UPDATE bt SET L={}, R=0 WHERE V={}".format(L, V))
    elif 70 < r and r <= 95:
        stmts.append("SELECT * WHERE V={}".format(L, V))
    else:
        stmts.append("UPDATE bt SET L={}, R=0 WHERE V={}".format(L, V))
    
    # config.candidate_record_id_list[V_idx] = config.candidate_record_id_list[-1]
    # config.candidate_record_id_list.pop()
    
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