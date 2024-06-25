from benchmark.ycsb import ycsbutils
import dejima
from dejima import Loader

class YCSBLoader(Loader):
    def _load(self, params):
        param_keys = ["start_id", "record_num", "step"]
        self.param_check(params, param_keys)

        start_id = int(params['start_id'])
        record_num = int(params['record_num'])
        step = int(params['step'])

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        # workload
        stmt = ycsbutils.get_stmt_for_load(start_id, record_num, step)

        # execution
        executer.execute_stmt(stmt)

        # propagation
        executer.propagate(is_load=True, DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result