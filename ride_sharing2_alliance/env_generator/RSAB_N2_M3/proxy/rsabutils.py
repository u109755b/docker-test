import random, string
import config
import threading

COL_N = 10
COND_N = 10

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def get_stmt_for_load(start_id, record_num, step):
    # prepare cols name
    col_names = ["V", "L", "D", "R"] + config.sorted_al_list + ["LINEAGE"]

    # create bulk insert statement
    stmt = "INSERT INTO bt (" + ",".join(col_names) + ") VALUES "
    records = []
    for i in range(start_id, start_id + record_num * step, step):
        cols = []
        
        cols.append(str(random.randint(1, 9999)))
        cols.append(str(random.randint(1, 9999)))
        cols.append('0')
        for j in range(len(config.sorted_al_list)):
            cols.append("'true'")
        
        record = "(" + ",".join([str(i)] + cols + ["'"+config.peer_name+"-bt-"+str(i)+"'"]) + ")"
        records.append(record)
        # config.candidate_record_ids.add(i)
        config.candidate_record_id_list.append(i)
    # config.candidate_record_id_list = list(config.candidate_record_ids)
    # config.candidate_record_id_list = [start_id]
        
    stmt = stmt + ",".join(records)
    return stmt

def get_workload_for_provider(updated_data_list):
    stmts = []
    # # Read
    # for i in range(read_num):
    #     target_col = 'col{}'.format(random.randint(1,COL_N))
    #     stmts.append("SELECT {} FROM bt WHERE id={}".format(target_col, next(zipf_gen)))
    # # Write
    # for i in range(write_num):
    #     target_col = 'col{}'.format(random.randint(1,COL_N))
    #     stmts.append("UPDATE bt SET {}='{}' WHERE id={}".format(target_col, randomname(10), next(zipf_gen)))
    t_type = ''
    if updated_data_list == []:
        stmt_num = 1
        # if len(config.candidate_record_id_list) < stmt_num:
        #     return [], 'transaction'
        for i in range(stmt_num):
            L = random.randint(1, 9999)
            V_idx = random.randint(1, len(config.candidate_record_id_list))-1
            V = config.candidate_record_id_list[V_idx]
            print(f"a = {config.candidate_record_id_list}, a[{V_idx}] = {V}")
            stmts.append("UPDATE bt SET L={}, R=0 WHERE V={}".format(L, V))
            # config.candidate_record_id_list[V_idx] = config.candidate_record_id_list[-1]
            # config.candidate_record_id_list.pop()
        t_type = 'transaction'
    else:
        for updated_data in updated_data_list:
            print(updated_data[0])
            stmts.append("UPDATE bt SET U='false' WHERE V={}".format(updated_data[0]))
            config.candidate_record_id_list.append(updated_data[0])
        t_type = 'detect_update'
    return stmts, t_type
    
def get_workload_for_alliance(updated_data_list):
    stmts = []
    t_type = ''
    if updated_data_list == []:
        stmt_num = 1
        # if len(config.candidate_record_id_list) < stmt_num:
        #     return [], 'transaction'
        for i in range(stmt_num):
            D = random.randint(1, 9999)
            V_idx = random.randint(1, len(config.candidate_record_id_list))-1
            V = config.candidate_record_id_list[V_idx]
            # print(f"a = {config.candidate_record_id_list}, a[{V_idx}] = {V}")
            stmts.append("UPDATE mt SET D={}, R=1 WHERE V={}".format(D, V))
            # config.candidate_record_id_list[V_idx] = config.candidate_record_id_list[-1]
            # config.candidate_record_id_list.pop()
        t_type = 'transaction'
    else:
        for updated_data in updated_data_list:
            print(updated_data[0])
            stmts.append("UPDATE mt SET U='false' WHERE V={}".format(updated_data[0]))
            config.candidate_record_id_list.append(updated_data[0])
        t_type = 'detect_update'
    return stmts, t_type

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