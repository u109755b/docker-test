import dejima
from dejima import config
from dejima import Loader
from benchmark import benchutils
from benchmark.tpcc import tpccutils
from benchmark.tpcc import tpcc_consts

class CustomerLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        p_id = config.p_id
        w_id = tpccutils.get_w_id(p_id)
        # w_p_n = tpccutils.get_w_p_n(w_id)
        # w_p_id = tpccutils.get_w_p_id(p_id)

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        c_n = tpcc_consts.RECORDS_NUM_CUSTOMER
        # p_c_n = benchutils.divide_into_k(c_n, w_p_n, w_p_id)
        c_batch_size = tpcc_consts.BATCH_SIZE_CUSTOMER
        c_batch_list = benchutils.divide_into_batch(c_n, c_batch_size, offset=1)

        d_id_list, p_id_list = tpccutils.get_d_id_p_id_list(p_id)
        for d_id in d_id_list:
            if p_id_list[0] != p_id: continue
            # customer, history
            for batch_offset, batch_size in zip(*c_batch_list):
                print(f"customer: {w_id}, {d_id}, {batch_offset}, {batch_size}")
                c_stmt, h_stmt = tpccutils.get_loadstmt_for_customer_history(w_id, d_id, batch_offset, batch_size)
                executer.execute_stmt(c_stmt)
                executer.execute_stmt(h_stmt)
                executer.propagate(DEBUG=True)

            # orders, neworders, orderline
            o_stmt, ol_stmt, no_stmt = tpccutils.get_loadstmt_for_orders_neworders_orderline(w_id, d_id)
            executer.execute_stmt(o_stmt)
            executer.execute_stmt(ol_stmt)
            executer.execute_stmt(no_stmt)
            executer.propagate(DEBUG=True)

        # propagation
        executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
