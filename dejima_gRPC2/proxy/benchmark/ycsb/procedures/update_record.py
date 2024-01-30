import random
import sqlparse
import dejima
from benchmark import benchutils
from benchmark.ycsb import ycsbutils
from dejima import GlobalBencher

class UpdateRecord(GlobalBencher):
    def _execute(self):
        # create executer
        executer = dejima.get_executer("bench")
        executer.create_tx()
        executer.set_params(self.params)

        stmt = self.get_stmt()
        where_clause = sqlparse.parse(stmt)[0][-1].value
        get_lineage_stmt = "SELECT lineage FROM bt {} FOR UPDATE NOWAIT".format(where_clause)


        # local lock
        lineages = []

        executer.execute_stmt(get_lineage_stmt)
        record = executer.fetchone()
        if not record:
            executer._restore()
            print("write miss")
            return "miss"
        lineages.append(record[0])

        # global lock
        if self.locking_method == "frs":
            executer.lock_global(lineages)

        # local execution
        executer.execute_stmt(stmt)

        # propagation
        executer.propagate(self.global_params)

        # termination
        commit = executer.terminate()

        return commit



    # create statement and return it
    def get_stmt(self):
        target_col = 'col{}'.format(random.randint(1,ycsbutils.COL_N))
        target_val = benchutils.randomname(10)
        ycsb_id = next(ycsbutils.zipf_gen)
        stmt = "UPDATE bt SET {}='{}' WHERE id={}".format(target_col, target_val, ycsb_id)
        return stmt