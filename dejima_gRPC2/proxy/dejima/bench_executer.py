import json
import time
import config
from transaction import Tx
import dejimautils
from dejima.executer import Executer

class BenchExecuter(Executer):
    # set params
    def set_params(self, benchmark_management, result_measurement, time_measurement, timestamp_management, timestamp):
        self.benchmark_management = benchmark_management
        self.result_measurement = result_measurement
        self.time_measurement = time_measurement
        self.timestamp_management = timestamp_management
        self.timestamp = timestamp

    # get member variables
    def get_global_xid(self):
        return self.global_xid
    def get_tx(self):
        return self.tx

    # lock global records
    def lock_global(self, lineages):
        error_occurred = False
        self.time_measurement.start_timer("global_lock", self.global_xid)
        self.result_measurement.start_global_lock()
        if config.prelock_request_invalid == False:
            try:
                result = super().lock_global(lineages)
            except Exception as e:
                error_occurred = True
                result = e
        self.time_measurement.stop_timer("global_lock", self.global_xid)
        self.result_measurement.finish_global_lock()

        self.timestamp.append(time.perf_counter())   # 1
        if error_occurred:
            raise result
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
    def terminate(self, DEBUG=False):
        commit_status_list = {}
        commit_status_list["2pl"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list["frs"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list = commit_status_list[self.locking_method]
        result = False
        if self.status in commit_status_list:
            result = True

        if result:
            self.time_measurement.start_timer("local_commit", self.global_xid)
            self.tx.commit()
            self.time_measurement.stop_timer("local_commit", self.global_xid)

            self.time_measurement.start_timer("global_commit", self.global_xid)
            dejimautils.termination_request("commit", self.global_xid, self.locking_method)
            self.time_measurement.stop_timer("global_commit", self.global_xid)

            self.result_measurement.commit_tx('update', self.global_params["max_hop"])
            msg = "commited"
        else:
            self.time_measurement.start_timer("local_abort", self.global_xid)
            self.tx.abort()
            self.time_measurement.stop_timer("local_abort", self.global_xid)

            self.time_measurement.start_timer("global_abort", self.global_xid)
            dejimautils.termination_request("abort", self.global_xid, self.locking_method)
            self.time_measurement.stop_timer("global_abort", self.global_xid)

            self.result_measurement.abort_tx('global', self.global_params["max_hop"])
            msg = "aborted"
        del config.tx_dict[self.global_xid]
        self.timestamp.append(time.perf_counter())   # 5

        if DEBUG: print("termination:", msg)
        # save timestamps
        if result:
            self.global_params["timestamps"].append(self.timestamp)
            self.timestamp_management.add_timestamps(self.global_params["timestamps"])

        return result
