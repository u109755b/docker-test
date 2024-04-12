import dejima
from dejima import config
from dejima import Loader
from dejima import utils
from benchmark.tpcc import tpccutils
from benchmark.tpcc import tpcc_consts

class LocalLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        p_n = int(params['peer_num'])
        p_id = int(params['peer_idx'])
        W_P_N = tpcc_consts.W_P_N
        config.p_n = p_n
        config.p_id = p_id
        config.w_n = (p_n-1) // W_P_N + 1
        config.w_id = tpccutils.get_w_id(p_id)

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()

        # load item
        executer.execute_stmt(tpccutils.get_loadstmt_for_item())

        # termination
        result = executer.terminate(DEBUG=True)
        return result
