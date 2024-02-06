import dejima
from dejima import config
from dejima import Loader
from benchmark.tpcc import tpccutils

class LocalLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        peer_num = int(params['peer_num'])
        config.warehouse_num = (peer_num-1) // 10 + 1

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()

        # load item
        executer.execute_stmt(tpccutils.get_loadstmt_for_item())

        # termination
        result = executer.terminate(DEBUG=True)
        return result
