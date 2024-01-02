import config
import dejimautils
from transaction import Tx

class TemplateLocal:
    def __init__():
        pass

    def execute(params, locking_method):
        if "benchmark_management" in params:
            benchmark_management = params["benchmark_management"]
        if "result_measurement" in params:
            result_measurement = params["result_measurement"]
        if "time_measurement" in params:
            time_measurement = params["time_measurement"]

        result_measurement.start_tx()

        # create new tx
        global_xid = dejimautils.get_unique_id()
        tx = Tx(global_xid)
        config.tx_dict[global_xid] = tx

        BenchTx = benchmark_management.get_tx()
        bench_tx = BenchTx(tx, {'global_xid': global_xid})


        # get local locks and check whether miss or not
        local_locks_result = bench_tx.get_local_locks()

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
        local_tx_result = bench_tx.execute_local_tx()

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
