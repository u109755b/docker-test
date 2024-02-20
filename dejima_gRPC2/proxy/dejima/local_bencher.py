import os
import time
from dejima import status
from dejima import errors

class LocalBencher:
    def _execute(self):
        # -- inherit this class and override this method --
        raise Exception("set _execute")

    def execute(self, params, locking_method):
        self.locking_method = locking_method

        self.result_measurement = params["result_measurement"]
        self.time_measurement = params["time_measurement"]
        self.timestamp_management = params["timestamp_management"]

        self.result_measurement.start_tx()

        try:
            result = self._execute()
        except errors.LocalLockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: local lock failed")
            self.result_measurement.abort_tx('local')
            return status.ABORTED
        except Exception as e:
            # errors.out_err(e, "global bencher error", out_trace=True)
            raise

        if result == status.COMMITTED:
            self.result_measurement.commit_tx("read")
        else:
            self.result_measurement.abort_tx("local", hop=1)

        return result
