import dejima
from dejima import Loader
from benchmark.tpcc import tpccutils
from benchmark.tpcc import tpcc_consts

class StockLoader(Loader):
    def _load(self, params):
        param_keys = ["peer_num", "peer_idx"]
        self.param_check(params, param_keys)

        peer_idx = int(params["peer_idx"])
        w_id = (peer_idx-1) // 10 + 1
        idx_in_group = (peer_idx-1) % 10 + 1

        # create executer
        executer = dejima.get_executer("load")
        executer.create_tx()
        executer.lock_global(['dummy'])

        # warehouse
        if peer_idx % 10 == 1:
            executer.execute_stmt(tpccutils.get_loadstmt_for_warehouse(w_id))
            executer.propagate(DEBUG=True)

        # district
        executer.execute_stmt(tpccutils.get_loadstmt_for_district(w_id, idx_in_group))
        executer.propagate(DEBUG=True)

        # stock
        stock_size = tpcc_consts.RECORDS_NUM_STOCK
        stock_batch_size = tpcc_consts.BATCH_SIZE_STOCK
        stock_peer_offset = (idx_in_group-1) * stock_size + 1

        for batch_offset in range(0, stock_size, stock_batch_size):
            items_size = stock_batch_size
            if stock_size - batch_offset < stock_batch_size:
                items_size = stock_size - batch_offset

            executer.execute_stmt(tpccutils.get_loadstmt_for_stock(w_id, stock_peer_offset + batch_offset, items_size))
            executer.propagate(DEBUG=True)

        # termination
        result = executer.terminate(DEBUG=True)
        return result
