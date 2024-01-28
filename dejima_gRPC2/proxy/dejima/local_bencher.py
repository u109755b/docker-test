import time
import dejima


class LocalBencher:
    def _execute(self):
        # -- inherit this class and override this method --
        raise Exception("set _execute")

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

        self.result_measurement.start_tx()

        try:
            commit = self._execute()
        except dejima.errors.LockNotAvailable as e:
            print("local lock failed")
            self.result_measurement.abort_tx('local')
            return False
        # except dejima.GlobalLockNotAvailable as e:
        #     print("global lock failed")
        #     self.result_measurement.abort_tx('global', 1)
        #     return False
        except Exception as e:
            # dejima.out_err(e, "global bencher error", out_trace=True)
            raise

        if commit == "commited":
            result = True
            self.result_measurement.commit_tx("read")
        else:
            result = False

        return result
