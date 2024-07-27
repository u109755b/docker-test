import time
import dejima.status
from dejima import config
from dejima import dejimautils
from dejima import requester
from dejima import errors
from dejima.executer import Executer

class BenchExecuter(Executer):
    # set params
    def set_params(self, params):
        self.result_measurement = params["result_measurement"]
        self.time_measurement = params["time_measurement"]
        self.timestamp_management = params["timestamp_management"]
        self.timestamp = params["timestamp"]
        self.tx_type = None
        if "tx_type" in params:
            self.tx_type = params["tx_type"]

        self.timestamp.append(time.perf_counter())   # 0
        self.result_measurement.start_tx(self.tx_type)

    # get member variables
    def get_global_xid(self):
        return self.global_xid
    def get_tx(self):
        return self.tx

    # lock global records
    def lock_global(self, lineages, locking_method):
        if locking_method == "2pl":
            self.timestamp.append(time.perf_counter())   # 1
            # if config.adr_mode:
            #     config.countup_request(lineages, "update", config.peer_name)
            return "Ack"

        self.time_measurement.start_timer("global_lock", self.global_xid)
        self.result_measurement.start_global_lock()

        if config.prelock_request_invalid == False:
            try:
                result = super().lock_global(lineages)
            finally:
                self.time_measurement.stop_timer("global_lock", self.global_xid)
                self.result_measurement.finish_global_lock()

        self.timestamp.append(time.perf_counter())   # 1
        return result


    # propagation
    def propagate(self, global_params={}, DEBUG=False):
        self.global_params = global_params
        self.timestamp.append(time.perf_counter())   # 2
        prop_dict = self.propagate_dejima_table()
        self.timestamp.append(time.perf_counter())   # 3
        result = self.propagate_other_peer(prop_dict, DEBUG)
        self.timestamp.append(time.perf_counter())   # 4
        return result


    # terminate
    def terminate(self, store_timestamps=True, DEBUG=False):
        commit_status_list = {}
        commit_status_list["2pl"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list["frs"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list = commit_status_list[self.locking_method]

        if self.status in commit_status_list:
            self.time_measurement.start_timer("local_commit", self.global_xid)
            self.tx.commit()
            self.time_measurement.stop_timer("local_commit", self.global_xid)

            self.time_measurement.start_timer("global_commit", self.global_xid)
            requester.termination_request("commit", self.global_xid, self.locking_method)
            self.time_measurement.stop_timer("global_commit", self.global_xid)

            self.result_measurement.commit_tx('update', hop=self.global_params["max_hop"])
            result = dejima.status.COMMITTED
            msg = "committed"
        else:
            self.time_measurement.start_timer("local_abort", self.global_xid)
            self.tx.abort()
            self.time_measurement.stop_timer("local_abort", self.global_xid)

            self.time_measurement.start_timer("global_abort", self.global_xid)
            requester.termination_request("abort", self.global_xid, self.locking_method)
            self.time_measurement.stop_timer("global_abort", self.global_xid)

            self.result_measurement.abort_tx('global', hop=self.global_params["max_hop"])
            result = dejima.status.ABORTED
            msg = "aborted"
        self.tx.close()
        self.timestamp.append(time.perf_counter())   # 5

        if DEBUG: print("termination:", msg)
        # save timestamps
        if result == dejima.status.COMMITTED and store_timestamps:
            self.global_params["timestamps"].append(self.timestamp)
            self.timestamp_management.add_timestamps(self.global_params["timestamps"])

        return result
