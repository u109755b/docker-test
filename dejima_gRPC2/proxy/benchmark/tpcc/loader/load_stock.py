import dejima
from dejima import config
from dejima import Loader
from dejima import utils
from benchmark import benchutils
from benchmark.tpcc import tpccutils
from benchmark.tpcc import tpcc_consts

class StockLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        p_id = config.p_id
        w_id = tpccutils.get_w_id(p_id)
        w_p_n = tpccutils.get_w_p_n(w_id)
        w_p_id = tpccutils.get_w_p_id(p_id)

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        # warehouse
        if w_p_id == 1:
            executer.execute_stmt(tpccutils.get_loadstmt_for_warehouse(w_id))
            executer.propagate(DEBUG=True)

        # district
        d_id_list, p_id_list = tpccutils.get_d_id_p_id_list(p_id)
        for d_id in d_id_list:
            if p_id_list[0] != p_id: continue
            print(f"district: {w_id}, {d_id}")
            executer.execute_stmt(tpccutils.get_loadstmt_for_district(w_id, d_id))
            executer.propagate(DEBUG=True)

        # stock
        s_size = tpcc_consts.RECORDS_NUM_STOCK
        s_batch_size = tpcc_consts.BATCH_SIZE_STOCK

        k_divider = utils.BaseDivider(s_size, w_p_n)
        p_s_size = k_divider.get_range_size(w_p_id)
        s_offset = k_divider.get_start(w_p_id)

        s_batch_list = benchutils.divide_into_batch(p_s_size, s_batch_size, offset=s_offset)
        for batch_offset, batch_size in zip(*s_batch_list):
            print(f"stock: {w_id}, {batch_offset}, {batch_size}")
            executer.execute_stmt(tpccutils.get_loadstmt_for_stock(w_id, batch_offset, batch_size))
            executer.propagate(DEBUG=True)


        # stock_size = tpcc_consts.RECORDS_NUM_STOCK
        # stock_batch_size = tpcc_consts.BATCH_SIZE_STOCK
        # stock_peer_offset = (w_p_id-1) * stock_size + 1

        # for batch_offset in range(0, stock_size, stock_batch_size):
        #     items_size = stock_batch_size
        #     if stock_size - batch_offset < stock_batch_size:
        #         items_size = stock_size - batch_offset

        #     executer.execute_stmt(tpccutils.get_loadstmt_for_stock(w_id, stock_peer_offset + batch_offset, items_size))
        #     executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
