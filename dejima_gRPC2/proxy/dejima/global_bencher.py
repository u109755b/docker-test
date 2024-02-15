import os
import time
import copy
from opentelemetry import trace
from dejima import config
from dejima import errors

tracer = trace.get_tracer(__name__)

class GlobalBencher:
    def _execute(self):
        # -- inherit this class and override this method --
        raise Exception("set _execute")

    @tracer.start_as_current_span("execute_bench_tx")
    def execute(self, params, locking_method):
        self.locking_method = locking_method

        self.result_measurement = params["result_measurement"]
        self.time_measurement = params["time_measurement"]
        self.timestamp_management = params["timestamp_management"]
        self.timestamp = []

        self.params = copy.copy(params)
        self.params["timestamp"] = self.timestamp

        self.timestamp.append(time.perf_counter())   # 0
        self.result_measurement.start_tx()

        # propagation to other peers
        self.global_params = {
            "max_hop": 1,
            "timestamps": [],
            "source_peer": config.peer_name,
        }


        try:
            commit = self._execute()
        except errors.LocalLockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: local lock failed")
            self.result_measurement.abort_tx('local')
            return False
        except errors.GlobalLockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: global lock failed")
            self.result_measurement.abort_tx('global', 1)
            return False
        except Exception as e:
            # errors.out_err(e, "global bencher error", out_trace=True)
            raise

        return commit
