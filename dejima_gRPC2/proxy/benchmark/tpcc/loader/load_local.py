import dejima
from dejima import config
from dejima import Loader
from benchmark.tpcc import tpccutils

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
        executer = dejima.get_executer("load")
        executer.create_tx()

        # execution
        executer.execute_stmt(tpccutils.get_loadstmt_for_item())

        # termination
        result = executer.terminate(DEBUG=True)
        return result
