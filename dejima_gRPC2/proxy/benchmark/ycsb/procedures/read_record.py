from benchmark.ycsb import ycsbutils

class ReadRecord:
    # initialize
    def __init__(self, tx, params=None):
        self.tx = tx


    # get local locks, and return lineages
    def get_local_locks(self):
        tx = self.tx

        self.stmt = self.get_stmt()
        lock_stmt = f"{self.stmt} FOR SHARE NOWAIT"

        try:
            tx.cur.execute(lock_stmt)
            res = tx.cur.fetchone()

            if not res:
                print("read_record.py: miss")
                return "miss"   # did not find the record
        except Exception as e:
            return False   # failed to get lock
        return True


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
        stmt = "SELECT * FROM bt WHERE id={}".format(next(ycsbutils.zipf_gen))
        return stmt