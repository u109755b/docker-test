import json
import time
from opentelemetry import trace
from transaction import Tx
import config
import dejima
import dejimautils

tracer = trace.get_tracer(__name__)

class GlobalBencher:
    def _execute(self):
        # -- inherit this class and override this method --
        raise Exception("set _execute")

    @tracer.start_as_current_span("execute_bench_tx")
    def execute(self, params, locking_method):
        self.locking_method = locking_method

        self.benchmark_management = None
        self.result_measurement = None
        self.time_measurement = None
        self.timestamp_management = None
        if "benchmark_management" in params:
            self.benchmark_management = params["benchmark_management"]
        if "result_measurement" in params:
            self.result_measurement = params["result_measurement"]
        if "time_measurement" in params:
            self.time_measurement = params["time_measurement"]
        if "timestamp_management" in params:
            self.timestamp_management = params["timestamp_management"]

        # propagation to other peers
        self.global_params = {
            "max_hop": 1,
            "timestamps": [],
            "source_peer": config.peer_name,
        }

        self.timestamp = []
        self.timestamp.append(time.perf_counter())   # 0
        self.result_measurement.start_tx()

        try:
            commit = self._execute()
        except dejima.errors.LockNotAvailable as e:
            print("local lock failed")
            self.result_measurement.abort_tx('local')
            return False
        except dejima.GlobalLockNotAvailable as e:
            print("global lock failed")
            self.result_measurement.abort_tx('global', 1)
            return False
        except Exception as e:
            # dejima.out_err(e, "global bencher error", out_trace=True)
            raise

        return commit
