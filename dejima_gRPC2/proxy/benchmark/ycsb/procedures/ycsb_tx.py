import random
import sqlparse
from benchmark import benchutils
from benchmark.ycsb import ycsbutils
import dejima
from dejima import GlobalBencher

class YCSBTx(GlobalBencher):
    def _execute(self):
        # create executer
        executer = dejima.get_executer("bench")
        executer.create_tx()
        self.params["tx_type"] = "read5_update5"
        executer.set_params(self.params)


        stmts = self.get_stmts(5, 5)

        # get local locks and get lineages
        lock_stmts = []
        get_lineage_stmts = []
        for stmt in stmts:
            if stmt.startswith("SELECT"):
                lock_stmts.append(stmt + " FOR SHARE NOWAIT")
            elif stmt.startswith("UPDATE"):
                where_clause = sqlparse.parse(stmt)[0][-1].value
                get_lineage_stmts.append("SELECT lineage FROM bt {} FOR UPDATE NOWAIT".format(where_clause))


        # local lock
        lineages = []

        # read
        for stmt in lock_stmts:
            executer.execute_stmt(stmt)
        # write
        for stmt in get_lineage_stmts:
            executer.execute_stmt(stmt)
            record = executer.fetchone()
            if not record:
                executer._restore()
                print("ycsb miss")
                return "miss"
            lineages.append(record[0])

        # global lock
        # if self.locking_method == "frs":
        executer.lock_global(lineages, self.locking_method)

        # local execution
        for stmt in stmts:
            executer.execute_stmt(stmt)

        # propagation
        executer.propagate(self.global_params)

        # termination
        commit = executer.terminate()

        return commit



    # create statement and return it
    def get_stmts(self, read_num, write_num):
        stmts = []
        # Read
        for _ in range(read_num):
            target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
            stmts.append("SELECT {} FROM bt WHERE id={}".format(target_col, next(ycsbutils.zipf_gen)))
        # Write
        for _ in range(write_num):
            target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
            target_val = benchutils.randomname(10)
            ycsb_id = next(ycsbutils.zipf_gen)
            stmts.append("UPDATE bt SET {}='{}' WHERE id={}".format(target_col, target_val, ycsb_id))
        return stmts