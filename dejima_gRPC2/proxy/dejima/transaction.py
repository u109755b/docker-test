import time
import re
from collections import defaultdict
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from dejima import errors
from dejima.pool import pool
from dejima import config

class Tx:
    def __init__(self, global_xid, start_time=None):
        self.global_xid = global_xid
        self.db_conn = pool.getconn(key=global_xid)
        self.db_conn.set_session(isolation_level=ISOLATION_LEVEL_READ_COMMITTED)   # default setting though
        self.child_peers = defaultdict(set)
        self.child_peers_all = set()
        self.cur = self.db_conn.cursor(cursor_factory=DictCursor)   # return DictRow instead of TupleRow
        self.start_time = start_time if start_time else time.perf_counter()
        self.propagation_cnt = 0
        self.is_terminated = False
        self.fetchone_result = None
        self.local_xid = None
        self.pid = None
        config.tx_dict[global_xid] = self
        config.pid_to_tx[self.get_pid()] = self

    def check_tx_existance(func):
        def _wrapper(self, *args, **kwargs):
            if self.is_terminated:
                raise errors.TxTerminated("this tx has already been terminated")
            return func(self, *args, **kwargs)
        return _wrapper

    def close(self):
        del config.tx_dict[self.global_xid]
        del config.pid_to_tx[self.pid]
        if self.global_xid in config.prop_visited:
            del config.prop_visited[self.global_xid]
        pool.putconn(self.db_conn)

    @check_tx_existance
    def commit(self):
        self.is_terminated = True
        self.cur.close()
        self.db_conn.commit()

    @check_tx_existance
    def abort(self):
        self.is_terminated = True
        self.cur.close()
        self.db_conn.rollback()

    def get_local_xid(self):
        if not self.local_xid:
            self.cur.execute("SELECT txid_current()")
            self.local_xid = self.cur.fetchone()[0]
        return self.local_xid

    def get_pid(self):
        if not self.pid:
            self.cur.execute("SELECT pg_backend_pid()")
            self.pid = self.cur.fetchone()[0]
        return self.pid

    # execute
    def execute(self, stmt, max_retry_cnt=0):
        self.fetchone_result = None
        self.cur.execute(stmt)
        if max_retry_cnt:
            result = self.cur.fetchone()
            retry_cnt = 0
            while not result and retry_cnt < max_retry_cnt:
                self.cur.execute(stmt)
                result = self.cur.fetchone()
                retry_cnt += 1
            self.fetchone_result = result
            if retry_cnt:
                if self.fetchone_result:
                    print(f'"{stmt}": retried {retry_cnt} out of {max_retry_cnt} times to get a result')
                else:
                    print(f'"{stmt}": failed to fetch a result after trying {retry_cnt} times')

    # fetchone
    def fetchone(self):
        """Returns:
        - success -> psycopg2.extras.DictRow   ex) [val1, val2, ...]
        - select non-existent record -> None
        - no result (INSERT, UPDATE, DELETE) -> raise psycopg2.ProgrammingError: no results to fetch
        """
        if self.fetchone_result:
            result = self.fetchone_result
            self.fetchone_result = None
        else:
            result = self.cur.fetchone()
        return result

    # fetchall
    def fetchall(self):
        """Returns:
        - success -> list   ex) [DictRow, DictRow, ...]
        - select non-existent record -> []
        """
        if self.fetchone_result:
            result = [self.fetchone_result] + self.cur.fetchall()
            self.fetchone_result = None
        else:
            result = self.cur.fetchall()
        return result

    def extend_childs(self, target_peers, prop_num):
        self.child_peers[prop_num] |= set(target_peers)

    def extend_childs_all(self, target_peers):
        self.child_peers_all |= set(target_peers)

    def reset_childs(self):
        self.child_peers = defaultdict(set)
        self.child_peers_all = set()
