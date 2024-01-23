import config
from benchmark.tpcc import tpccutils
import dejima
from dejima import Loader

class StockLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        # create executer
        executer = dejima.get_executer()
        executer.create_tx()
        executer.lock_global(['dummy'])

        w_id = (params["peer_idx"]-1) // 10 + 1
        start_id = (params["peer_idx"]-1) * 10000 + 1
        overall_size = 1000
        batch_size = 500

        for offset in range(0, overall_size, batch_size):
            # items_size
            if overall_size - offset < batch_size:
                items_size = overall_size - offset
            else:
                items_size = batch_size

            # execution and propagation
            executer.execute_stmt(tpccutils.get_loadstmt_for_stock(w_id, start_id+offset, items_size))
            executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
