import dejimautils
import config
from transaction import Tx
import json
import time
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class TemplateGlobal:
    def __init__(self):
        pass

    @tracer.start_as_current_span("execute_bench_tx")
    def execute(self, params, locking_method):
        if "benchmark_management" in params:
            benchmark_management = params["benchmark_management"]
        if "result_measurement" in params:
            result_measurement = params["result_measurement"]
        if "time_measurement" in params:
            time_measurement = params["time_measurement"]
        if "timestamp_management" in params:
            timestamp_management = params["timestamp_management"]

        result_measurement.start_tx()

        timestamp = []
        timestamp.append(time.perf_counter())   # 0

        # create new tx
        global_xid = dejimautils.get_unique_id()
        tx = Tx(global_xid)
        config.tx_dict[global_xid] = tx

        BenchTx = benchmark_management.get_tx()
        bench_tx = BenchTx(tx, {'global_xid': global_xid})


        # get local locks, check whether miss or not, and get lineages
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

        lineages = local_locks_result


        # lock request
        if locking_method == "frs":
            time_measurement.start_timer("global_lock", global_xid)
            result_measurement.start_global_lock()
            if config.prelock_request_invalid == False:
                if not lineages == []:
                    result = dejimautils.lock_request(lineages, global_xid)
                else:
                    result = "Ack"
            else: result = "Ack"
            time_measurement.stop_timer("global_lock", global_xid)
            result_measurement.finish_global_lock()

            if result != "Ack":
                # abort during global lock, release lock
                dejimautils.release_lock_request(global_xid) 
                tx.abort()
                del config.tx_dict[global_xid]
                result_measurement.abort_tx('global', 1)
                return False


        # local execution
        timestamp.append(time.perf_counter())   # 1
        local_tx_result = bench_tx.execute_local_tx()

        if local_tx_result == False:
            # abort during local execution
            if locking_method == "frs": dejimautils.release_lock_request(global_xid) 
            tx.abort()
            del config.tx_dict[global_xid]
            result_measurement.abort_tx('local')
            return False


        # propagation to the dejima table
        timestamp.append(time.perf_counter())   # 2
        try:
            tx.cur.execute("SELECT txid_current()")
            local_xid, *_ = tx.cur.fetchone()
            prop_dict = {}
            for dt in config.dt_list:
                target_peers = list(config.dejima_config_dict['dejima_table'][dt])
                target_peers.remove(config.peer_name)
                if target_peers == []: continue

                for bt in config.bt_list:
                    tx.cur.execute("SELECT {}_propagate_updates_to_{}()".format(bt, dt))
                tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
                delta, *_ = tx.cur.fetchone()

                if delta == None: continue
                delta = json.loads(delta)

                prop_dict[dt] = {}
                prop_dict[dt]['peers'] = target_peers
                prop_dict[dt]['delta'] = delta

                tx.extend_childs(target_peers)

        except Exception as e:
            # abort during getting BIRDS result
            print('error during BIRDS: ', e)
            if locking_method == "frs": dejimautils.release_lock_request(global_xid)
            tx.abort()
            del config.tx_dict[global_xid]
            return False


        # propagation to other peers
        global_params = {
            "max_hop": 1,
            "timestamps": [],
            "source_peer": config.peer_name,
        }

        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, global_xid, locking_method, global_params)
        else:
            result = "Ack"

        if result != "Ack":
            commit = False
        else:
            commit = True
        timestamp.append(time.perf_counter())   # 4


        # termination
        if commit:
            time_measurement.start_timer("local_commit", global_xid)
            tx.commit()
            time_measurement.stop_timer("local_commit", global_xid)

            time_measurement.start_timer("global_commit", global_xid)
            dejimautils.termination_request("commit", global_xid, locking_method)
            time_measurement.stop_timer("global_commit", global_xid)

            result_measurement.commit_tx('update', global_params["max_hop"])
        else:
            time_measurement.start_timer("local_abort", global_xid)
            tx.abort()
            time_measurement.stop_timer("local_abort", global_xid)

            time_measurement.start_timer("global_abort", global_xid)
            dejimautils.termination_request("abort", global_xid, locking_method)
            time_measurement.stop_timer("global_abort", global_xid)

            result_measurement.abort_tx('global', global_params["max_hop"])
        del config.tx_dict[global_xid]

        timestamp.append(time.perf_counter())   # 5


        # save timestamps
        if commit:
            global_params["timestamps"].append(timestamp)
            timestamp_management.add_timestamps(global_params["timestamps"])

        return commit
