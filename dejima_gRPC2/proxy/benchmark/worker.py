import time
import random
from collections import defaultdict
from dejima import measurement
from dejima import status

class Worker():
    def __init__(self):
        pass

    def execute(self, params):
        param_keys = ["bench_time", "method"]
        for key in param_keys:
            if not key in params.keys():
                res_dic = {"result": "Invalid parameters"}
                return res_dic
        bench_time = int(params['bench_time'])
        METHOD = params['method']
        benchmark_management = params['benchmark_management']

        # create time management instances
        result_measurement = measurement.ResultMeasurement()
        time_measurement = measurement.TimeMeasurement()
        timestamp_management = measurement.TimestampManagement()
        params = {
            "result_measurement": result_measurement,
            "time_measurement": time_measurement,
            "timestamp_management": timestamp_management
        }


        # benchmark
        start_time = time.time()
        print("benchmark start")
        random.seed()

        # frs & 2pl
        if METHOD == "frs" or METHOD == "2pl":
            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time
                TransactionClass = benchmark_management.get_tx_class()
                transaction = TransactionClass()
                result = transaction.execute(params, METHOD)

                # # cool down time
                # if result == status.ABORTED:
                #     time.sleep(0.005)

        # hybrid
        elif METHOD == "hybrid":
            current_method = "2pl"
            check_time = 30
            check_interval = 300
            next_check = random.randint(0,check_interval - check_time * 2)   # determine first check timing

            temp_commit = {"before": defaultdict(lambda: 0), "after": defaultdict(lambda: 0)}

            switch_method = lambda method: "frs" if method=="2pl" else "2pl"

            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time
                TransactionClass = benchmark_management.get_tx_class()
                transaction = TransactionClass()

                # normal mode
                if current_time < next_check:
                    result = transaction.execute(params, current_method)

                # check mode
                # before
                elif current_time < next_check + check_time:
                    result = transaction.execute(params, current_method)
                    temp_commit["before"][result] += 1
                # after
                elif current_time < next_check + check_time * 2:
                    result = transaction.execute(params, switch_method(current_method))
                    temp_commit["after"][result] += 1

                # return to normal, don't execute Tx
                else:
                    next_check += check_interval
                    before_commit_num = temp_commit["before"][status.COMMITTED]
                    after_commit_num = temp_commit["after"][status.COMMITTED]

                    if before_commit_num < after_commit_num:
                        print(f"{current_method}: {current_method} ({before_commit_num}) -> {switch_method(current_method)} ({after_commit_num})")
                        current_method = switch_method(current_method)

                    temp_commit = {"before": defaultdict(lambda: 0), "after": defaultdict(lambda: 0)}

                # # cool down time
                # if result == status.ABORTED:
                #     time.sleep(0.005)

        # invalid method
        else:
            res_dic = {"result": "invalid method"}
            return res_dic


        # get results
        res_dic = {"result": "success"}
        res_dic1 = time_measurement.get_result(display=True)
        res_dic2 = measurement.time_measurement.get_result(display=True)
        res_dic.update(**res_dic1, **res_dic2)
        res_dic["basic_res"] = result_measurement.get_result(display=True)
        res_dic["process_time"] = timestamp_management.get_result(display=True)

        print("benchmark finished")
        return res_dic
