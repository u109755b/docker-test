import random
import sqlparse
from benchmark import benchutils
from benchmark.ycsb import ycsbutils

class UpdateRecord:
    # initialize
    def __init__(self, tx, params=None):
        self.tx = tx


    # get local locks, and return lineages
    def get_local_locks(self):
        tx = self.tx
        lineages = []

        self.stmt = self.get_stmt()
        where_clause = sqlparse.parse(self.stmt)[0][-1].value
        get_lineage_stmt = "SELECT lineage FROM bt {} FOR UPDATE NOWAIT".format(where_clause)

        try:
            tx.cur.execute(get_lineage_stmt)
            lineage = tx.cur.fetchone()[0]   # DictRow type: ex) ['Peer1-bt-1']
            lineages.append(lineage)

        except Exception as e:
            return False   # failed to get lock
        return lineages


    # execute local transacion
    def execute_local_tx(self):
        tx = self.tx
        stmt = self.stmt

        try:
            tx.cur.execute(stmt)

        except:
            return False
        return True


    # create statement and return it
    def get_stmt(self):
        target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
        target_val = benchutils.randomname(10)
        ycsb_id = next(ycsbutils.zipf_gen)
        stmt = "UPDATE bt SET {}='{}' WHERE id={}".format(target_col, target_val, ycsb_id)
        return stmt