import dejimautils
import config
from transaction import Tx
from benchmark.tpcc_no_tx import TPCCNOTx
import tpccutils
import random
from datetime import datetime

def doTPCC_NO(params, locking_method):
    if "result_measurement" in params:
        result_measurement = params["result_measurement"]
    if "time_measurement" in params:
        time_measurement = params["time_measurement"]

    result_measurement.start_tx()

    # create new tx
    global_xid = dejimautils.get_unique_id()
    tx = Tx(global_xid)
    config.tx_dict[global_xid] = tx

    tpcc_no_tx = TPCCNOTx(tx)


    # get local locks and check whether miss or not
    local_locks_result = tpcc_no_tx.get_local_locks()

    if local_locks_result == False:
        # abort during local lock
        tx.abort()
        del config.tx_dict[global_xid]
        result_measurement.abort_tx('local')
        return False

    if local_locks_result == "miss":
        tx.abort()
        del config.tx_dict[global_xid]
        return "miss"


    # local execution
    local_tx_result = tpcc_no_tx.execute_local_tx()

    if local_tx_result == False:
        # abort during local execution
        tx.abort()
        del config.tx_dict[global_xid]
        result_measurement.abort_tx('local')
        return False


    tx.commit()
    result_measurement.commit_tx('read')
    del config.tx_dict[global_xid]

    return True
