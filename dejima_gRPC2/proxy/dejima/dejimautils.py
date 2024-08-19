import time
import threading
import uuid
import json
from datetime import datetime
from dejima import status
from dejima import errors
from dejima import config
from dejima.transaction import Tx


def get_unique_id():
    return config.peer_name + '-' + str(uuid.uuid4())

def get_tx(global_xid, start_time=None):
    if global_xid not in config.tx_dict:
        if start_time: tx = Tx(global_xid, start_time)
        else: raise TypeError("start_time is None")
    else:
        tx = config.tx_dict[global_xid]
    return tx

def execute_threads(thread_list):
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()

def json_converter(o):
    if isinstance(o, set):
        return list(o)
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')


# base lock
def base_lock(tx, lock_stmts, max_retry_cnt, min_miss_cnt, nowait):
    miss_cnt = 0
    miss_flag = False

    for lock_stmt in lock_stmts:
        lock_stmt = lock_stmt.rstrip(" \t\n;")
        if lock_stmt.endswith("NOWAIT"):
            lock_stmt = lock_stmt[:-len("NOWAIT")].rstrip()
        if nowait:
            lock_stmt = lock_stmt + " NOWAIT"

        tx.execute(lock_stmt, max_retry_cnt=max_retry_cnt)

        if min_miss_cnt >= 0 and not tx.fetchone():
            miss_cnt += 1
        if min_miss_cnt > 0 and miss_cnt >= min_miss_cnt:
            miss_flag = True
            break
        if min_miss_cnt == 0 and miss_cnt == len(lock_stmts):
            miss_flag = True
            break

    if miss_flag:
        return status.MISSED
    else:
        return status.LOCKED

# lock with wait
def lock_with_wait(th_lock, results, tx, lock_stmts, max_retry_cnt, min_miss_cnt):
    try:
        result = base_lock(tx, lock_stmts, max_retry_cnt, min_miss_cnt, nowait=False)
        with th_lock: results.append(result)
        while True:
            with th_lock:
                if len(results) == 2: break
            time.sleep(0.0005)
    except errors.QueryCanceled as e:
        with th_lock: results.append(status.DIED)

# check lock stats to kill process
def check_to_kill(th_lock, results, tx, attempting_tx):
    kill = False
    while not kill:
        time.sleep(0.001)
        with th_lock:
            if len(results): break

        tx.execute(f"SELECT pg_blocking_pids({attempting_tx.get_pid()})")   # 0.2[ms] ~ 2[ms]
        pid_list = tx.fetchone()[0]   # ~ 0.1[ms]

        with th_lock:   # 0[ms]
            if len(results): break

        for blocking_pid in pid_list:
            if blocking_pid not in config.pid_to_tx: continue
            blocking_tx = config.pid_to_tx[blocking_pid]
            if blocking_tx.start_time <= attempting_tx.start_time:   # if blocking tx is older or same
                kill = True
                break

    if kill:
        tx.execute(f"SELECT pg_cancel_backend({attempting_tx.get_pid()})")
        with th_lock: results.append("kill_requested")
    else:
        with th_lock: results.append("finished")

    tx.abort()
    tx.close()

# lock with wait-die
def lock_with_wait_die(tx, lock_stmts, max_retry_cnt, min_miss_cnt):
    if not lock_stmts: return
    check_tx = Tx(get_unique_id())
    th_lock = threading.Lock()
    results = []
    lock_tx = tx

    lock_thread = threading.Thread(target=lock_with_wait, args=([th_lock, results, lock_tx, lock_stmts, max_retry_cnt, min_miss_cnt]))
    check_thread = threading.Thread(target=check_to_kill, args=([th_lock, results, check_tx, lock_tx]))
    execute_threads([lock_thread, check_thread])

    if status.MISSED in results:
        print("miss occurred on another peer")
        raise errors.RecordsNotFound
    if status.DIED in results:
        raise errors.LockNotAvailable

# lock with no-wait
def lock_with_nowait(tx, lock_stmts, max_retry_cnt, min_miss_cnt):
    result = base_lock(tx, lock_stmts, max_retry_cnt, min_miss_cnt, nowait=True)
    if result == status.MISSED:
        print("miss occurred on another peer")
        raise errors.RecordsNotFound

# lock records
def lock_records(tx, lock_stmts, max_retry_cnt=0, min_miss_cnt=1, wait_die=False):
    """
    min_miss_cnt
    - 0: raise dejima.errors.RecordsNotFound when all lock stmts fail to fetch
    - > 1: raise dejima.errors.RecordsNotFound when max_retry_cnt stmts fail to fetch
    - < 0: disable this option (do not check if stmts fail to fetch)

    Raise List
    - dejima.errors.LockNotAvailable
    - dejima.errors.RecordsNotFound
    """
    if wait_die:
        lock_with_wait_die(tx, lock_stmts, max_retry_cnt, min_miss_cnt)
    else:
        lock_with_nowait(tx, lock_stmts, max_retry_cnt, min_miss_cnt)



# get condition
def get_where_condition(table_name, lineages):
    if type(lineages) is str:
        lineages = [lineages]
    if table_name == "d_customer":
        lineage_col_name = "c_lineage"   # hardcode (lineage name)
    else:
        lineage_col_name = "lineage"
    condition = " OR ".join([f"{lineage_col_name} = '{lineage}'" for lineage in lineages])
    return lineage_col_name, condition

# get lock statements for lock records of dejima tables
def get_lock_stmts(json_data):
    lock_stmts = []
    json_dict = json_data
    for delete in json_dict["deletions"]:
        where = []
        for column, value in delete.items():
            if column != "lineage": continue
            if column=='txid': continue
            if not value and value != 0: continue   # NULL
            if type(value) is str:
                where.append(f"{column}='{value}'")
            else:
                where.append(f"{column}={value}")
        where = " AND ".join(where)
        lock_stmts.append("SELECT * FROM {} WHERE {} FOR UPDATE".format(json_dict["view"], where))
    return lock_stmts

# get execute statement for updating records of dejima tables
def get_execute_stmt(json_data, local_xid):
    sql_statements = []
    json_dict = json_data

    for delete in json_dict["deletions"]:
        where = []
        for column, value in delete.items():
            if column != "lineage": continue
            if column=='txid': continue
            if not value and value != 0: continue   # NULL
            if type(value) is str:
                where.append(f"{column}='{value}'")
            else:
                where.append(f"{column}={value}")
        where = " AND ".join(where)
        sql_statements.append("DELETE FROM {} WHERE {} RETURNING true".format(json_dict["view"], where))

    for insert in json_dict["insertions"]:
        columns = []
        values = []
        for column, value in insert.items():
            if column=='txid': continue
            columns.append(f"{column}")
            if not value and value != 0:
                values.append("NULL")
            elif type(value) is str:
                values.append(f"'{value}'")
            else:
                values.append(f"{value}")
        columns = "({})".format(", ".join(columns))
        values = "({})".format(", ".join(values))
        sql_statements.append("INSERT INTO {} {} VALUES {} RETURNING true".format(json_dict["view"], columns, values))
        
    update_stmts = []
    for i, stmt in enumerate(sql_statements):
        update_stmts.append("updated{} AS ({})".format(i, stmt))
    # print(local_xid)
    update_stmts.append("prop_to_bt AS (SELECT {}_propagate({}))".format(json_dict["view"], local_xid))
    update_stmts = "WITH " + ", ".join(update_stmts)
    union_stmts = []
    for i, _ in enumerate(sql_statements):
        union_stmts.append("SELECT * FROM updated{}".format(i))
    union_stmts.append("SELECT * FROM prop_to_bt")
    union_stmts = " UNION ".join(union_stmts)
    execute_stmt = update_stmts + union_stmts

    return execute_stmt


# lock with lineages
def lock_with_lineages(tx, lineages, for_what="SHARE"):
    # lineage_set
    if type(lineages) is str:
        lineages = [lineages]
    lineage_set = set(lineages) - {"dummy"}
    if not lineage_set: return

    # lock_stmts
    lock_stmts = []
    for bt in config.bt_list_all:
        lineage_col_name, condition = get_where_condition(bt, lineage_set)
        lock_stmt = f"SELECT {lineage_col_name} FROM {bt} WHERE {condition} FOR {for_what}"
        lock_stmts.append(lock_stmt)

    # lock with lineages
    lock_records(tx, lock_stmts, max_retry_cnt=0, min_miss_cnt=-1, wait_die=True)


# get timestamp
def get_timestamp(tx, lineage, to_isoformat=False):
    for bt in config.bt_list_all:
        lineage_col_name, condition =  get_where_condition(bt, lineage)
        tx.execute(f"SELECT updated_at FROM {bt} WHERE {condition}")
        local_timestamp, *_ = tx.fetchone()
        if not local_timestamp: continue
        if to_isoformat:
            local_timestamp = local_timestamp.isoformat()
        return local_timestamp
    print("get_timestamp failed")
    raise Exception("get_timestamp failed")


# execute fetch
def execute_fetch(execute, local_xid, latest_data_dict):
    for dt, delta in latest_data_dict.items():
        if dt not in config.dt_list: continue
        if "update" in delta:
            for latest_data in delta["update"]:
                lineage = latest_data[-3]
                lineage_col_name, condition =  get_where_condition(dt, lineage)
                execute(f"DELETE FROM {dt} WHERE {condition}")
                values = ", ".join(repr(value) for value in latest_data)
                execute(f"INSERT INTO {dt} VALUES ({values})")
            execute(f"SELECT {dt}_propagate({local_xid})")
        if "deletions" in delta or "insertions" in delta:
            stmt = get_execute_stmt(delta, local_xid)
            execute(stmt)


# propagate to dt
def propagate_to_dt(tx, dt, local_xid):
    for bt in config.bt_list[dt]:
        tx.execute("SELECT {}_propagates_to_{}({})".format(bt, dt, local_xid))
    tx.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
    delta, *_ = tx.fetchone()
    tx.execute("SELECT public.remove_dummy_{}({})".format(dt, local_xid))
    if delta == None: return {}
    return json.loads(delta)
