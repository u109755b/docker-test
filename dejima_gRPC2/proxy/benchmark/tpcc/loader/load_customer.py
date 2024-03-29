import dejima
from dejima import Loader
from benchmark.tpcc import tpccutils
from benchmark.tpcc import tpcc_consts

class CustomerLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        peer_idx = int(params["peer_idx"])
        w_id = (peer_idx-1) // 10 + 1
        d_id = (peer_idx-1) % 10 + 1

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        # customer, history
        customer_size = tpcc_consts.RECORDS_NUM_CUSTOMER
        customer_batch_size = tpcc_consts.BATCH_SIZE_CUSTOMER
        customer_peer_offset = 1

        for batch_offset in range(0, customer_size, customer_batch_size):
            items_size = customer_batch_size
            if customer_size - batch_offset < customer_batch_size:
                items_size = customer_size - batch_offset

            c_stmt, h_stmt = tpccutils.get_loadstmt_for_customer_history(w_id, d_id, customer_peer_offset + batch_offset, items_size)
            executer.execute_stmt(c_stmt)
            executer.execute_stmt(h_stmt)
            executer.propagate(DEBUG=True)

        # orders, neworders, orderline
        o_stmt, ol_stmt, no_stmt = tpccutils.get_loadstmt_for_orders_neworders_orderline(w_id, d_id)
        executer.execute_stmt(o_stmt)
        executer.execute_stmt(ol_stmt)
        executer.execute_stmt(no_stmt)

        # propagation
        executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
