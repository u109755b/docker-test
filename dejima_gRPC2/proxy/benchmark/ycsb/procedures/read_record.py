import dejima
from benchmark.ycsb import ycsbutils
from dejima import LocalBencher

class ReadRecord(LocalBencher):
    def _execute(self):
        # create executer
        executer = dejima.get_executer()
        executer.create_tx()

        stmt = self.get_stmt()
        lock_stmt = f"{stmt} FOR SHARE NOWAIT"


        # local lock
        lineages = []

        executer.execute_stmt(lock_stmt)
        record = executer.fetchone()
        if not record:
            executer._restore()
            print("read miss")
            return "miss"
        lineages.append(record[0])

        # global lock
        # if self.locking_method == "frs":
        #     executer.lock_global(lineages)

        # local execution
        executer.execute_stmt(stmt)

        # propagation
        # executer.propagate(self.global_params)

        # termination
        commit = executer.terminate()

        return commit



    # create statement and return it
    def get_stmt(self):
        stmt = "SELECT * FROM bt WHERE id={}".format(next(ycsbutils.zipf_gen))
        return stmt