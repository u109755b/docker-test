import random
import sqlparse
from benchmark import benchutils
from benchmark.ycsb import ycsbutils

class YCSBTx:
    # initialize
    def __init__(self, tx, params=None):
        self.tx = tx


    # get local locks, and return lineages
    def get_local_locks(self):
        tx = self.tx

        # workload
        self.stmts = self.get_stmts(5, 5)

        # get local locks and get lineages
        lock_stmts_for_read = []
        get_lineage_stmts = []
        for stmt in self.stmts:
            if stmt.startswith("SELECT"):
                lock_stmts_for_read.append(stmt + " FOR SHARE NOWAIT")
            elif stmt.startswith("UPDATE"):
                where_clause = sqlparse.parse(stmt)[0][-1].value
                get_lineage_stmts.append("SELECT lineage FROM bt {} FOR UPDATE NOWAIT".format(where_clause))
        try:
            miss_flag = True
            lineages = []
            for stmt in lock_stmts_for_read:
                tx.cur.execute(stmt)
                if tx.cur.fetchone() != None:
                    miss_flag = False
            for stmt in get_lineage_stmts:
                tx.cur.execute(stmt)
                try:
                    lineage, *_ = tx.cur.fetchone()
                    lineages.append(lineage)
                except:
                    continue
            if lineages != []:
                miss_flag = False

        except:
            return False
        if miss_flag:
            return "miss"
        return lineages


    # execute local transacion
    def execute_local_tx(self):
        tx = self.tx
        stmts = self.stmts

        try:
            for stmt in stmts:
                tx.cur.execute(stmt)

        except:
            return False
        return True


    # create statement and return it
    def get_stmts(self, read_num, write_num):
        stmts = []
        # Read
        for i in range(read_num):
            target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
            stmts.append("SELECT {} FROM bt WHERE id={}".format(target_col, next(ycsbutils.zipf_gen)))
        # Write
        for i in range(write_num):
            target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
            target_val = benchutils.randomname(10)
            ycsb_id = next(ycsbutils.zipf_gen)
            stmts.append("UPDATE bt SET {}='{}' WHERE id={}".format(target_col, target_val, ycsb_id))
        return stmts