import config
from benchmark.tpcc import tpccutils
import dejima
from dejima import Loader

class StockLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        peer_idx = int(params["peer_idx"])
        w_id = (peer_idx-1) // 10 + 1
        start_id = (peer_idx-1) * 10000 + 1
        overall_size = 1000
        batch_size = 500


        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        # warehouse
        for w_id in range(1, config.warehouse_num+1):
            if peer_idx % 10 == 1:
                executer.execute_stmt(tpccutils.get_loadstmt_for_warehouse(w_id))
        executer.propagate(DEBUG=True)

        # district
        for w_id in range(1, config.warehouse_num+1):
            executer.execute_stmt(tpccutils.get_loadstmt_for_district(w_id))
        executer.propagate(DEBUG=True)

        # stock
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
