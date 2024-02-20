import time
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from dejima import errors
from dejima.pool import pool

class Tx:
    def __init__(self, global_xid, start_time=None):
        self.global_xid = global_xid
        self.db_conn = pool.getconn(key=global_xid)
        self.db_conn.set_session(isolation_level=ISOLATION_LEVEL_READ_COMMITTED)   # default setting though
        self.child_peers = set()
        self.cur = self.db_conn.cursor(cursor_factory=DictCursor)   # return DictRow instead of TupleRow
        self.propagation_cnt = 0
        self.is_terminated = False
        self.local_xid = None
        self.pid = None
        self.start_time = start_time if start_time else time.perf_counter()

    def check_tx_existance(func):
        def _wrapper(self, *args, **kwargs):
            if self.is_terminated:
                raise errors.TxTerminated("this tx has already been terminated")
            return func(self, *args, **kwargs)
        return _wrapper

    @check_tx_existance
    def commit(self):
        self.is_terminated = True
        self.cur.close()
        self.db_conn.commit()
        pool.putconn(self.db_conn)

    @check_tx_existance
    def abort(self):
        self.is_terminated = True
        self.cur.close()
        self.db_conn.rollback()
        pool.putconn(self.db_conn)

    @check_tx_existance
    def get_local_xid(self):
        if not self.local_xid:
            self.cur.execute("SELECT txid_current()")
            self.local_xid = self.cur.fetchone()[0]
        return self.local_xid

    @check_tx_existance
    def get_pid(self):
        if not self.pid:
            self.cur.execute("SELECT pg_backend_pid()")
            self.pid = self.cur.fetchone()[0]
        return self.pid

    def extend_childs(self, target_peers):
        self.child_peers |= set(target_peers)

    def reset_childs(self):
        self.child_peers = set()