import config
from benchmark.tpcc import tpccutils
import dejima
from dejima import Loader

class CustomerLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num"]
        self.param_check(params, param_keys)

        # create executer
        executer = dejima.get_executer()
        executer.create_tx()
        executer.lock_global(['dummy'])

        # execution
        w_id = (int(config.peer_name.strip("Peer")) - 1) // 10 + 1
        d_id = (int(config.peer_name.strip("Peer")) - 1) % 10 + 1
        c_stmt, h_stmt = tpccutils.get_loadstmt_for_customer_history(w_id, d_id)
        executer.execute_stmt(c_stmt)
        executer.execute_stmt(h_stmt)
        o_stmt, ol_stmt, no_stmt = tpccutils.get_loadstmt_for_orders_neworders_orderline(w_id, d_id)
        executer.execute_stmt(o_stmt)
        executer.execute_stmt(ol_stmt)
        executer.execute_stmt(no_stmt)

        # propagation
        executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
