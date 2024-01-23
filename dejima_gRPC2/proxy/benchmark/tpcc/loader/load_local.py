import config
from benchmark.tpcc import tpccutils
import dejima
from dejima import Loader

class LocalLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        peer_num = int(params['peer_num'])
        if peer_num % 10 != 0:
            warehouse_num = peer_num // 10 + 1
        else:
            warehouse_num = int(peer_num / 10)
        config.warehouse_num = warehouse_num

        # create executer
        executer = dejima.get_executer()
        executer.create_tx()

        # execution
        for w_id in range(1, warehouse_num+1):
            executer.execute_stmt(tpccutils.get_loadstmt_for_warehouse(w_id))
        executer.execute_stmt(tpccutils.get_loadstmt_for_item())
        # w_id = (params["peer_idx"]-1) // 10 + 1
        # start_id = (params["peer_idx"]-1) * 10000 + 1
        # executer.execute_stmt(tpccutils.get_loadstmt_for_stock(w_id, start_id))
        for w_id in range(1, warehouse_num+1):
            executer.execute_stmt(tpccutils.get_loadstmt_for_district(w_id))

        # termination
        result = executer.terminate(DEBUG=True)
        return result
