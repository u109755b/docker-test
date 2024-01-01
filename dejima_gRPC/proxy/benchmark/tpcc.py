import json
import time
import config
import random
from benchmark.do_tpcc_no_tx import doTPCC_NO
from benchmark.do_tpcc_pay_tx import doTPCC_PAY
import data_pb2
import data_pb2_grpc

# class TPCC(object):
class TPCC(data_pb2_grpc.TPCCServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        # get params
        params = json.loads(req.json_str)
        param_keys = ["bench_time", "method"]
        for key in param_keys:
            if not key in params.keys():
                res_dic = {"result": "Invalid parameters"}
                return data_pb2.Response(json_str=json.dumps(res_dic))
        bench_time = int(params['bench_time'])
        METHOD = params['method']

        # create time management instances
        result_measurement = config.ResultMeasurement()
        time_measurement = config.TimeMeasurement()
        timestamp_management = config.TimestampManagement()
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
                if random.randint(1,100) < 0:
                    doTPCC = doTPCC_NO
                else:
                    doTPCC = doTPCC_PAY
                result = doTPCC(params, METHOD)

        # hybrid
        elif METHOD == "hybrid":
            current_method = "2pl"
            check_time = 30
            check_interval = 300
            next_check = random.randint(0,check_interval - check_time * 2)   # determine first check timing

            temp_commit = {'before': {'commit': 0, 'abort': 0}, 'after': {'commit': 0, 'abort': 0}}
            temp_changed_mode_flag = False

            switch_method = lambda method: 'frs' if method=='2pl' else '2pl'

            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time

                if random.randint(1,100) < 50:
                    doTPCC = doTPCC_NO
                else:
                    doTPCC = doTPCC_PAY

                # normal mode
                if current_time < next_check:
                    result = doTPCC(params, current_method)

                # check mode
                # before
                elif current_time < next_check + check_time:
                    result = doTPCC(params, current_method)
                    if result == True:
                        temp_commit['before']['commit'] += 1
                    elif result == False:
                        temp_commit['before']['abort'] += 1
                # after
                elif current_time < next_check + check_time * 2:
                    # change method if this is first time
                    if not temp_changed_mode_flag:
                        temp_changed_mode_flag = True
                        current_method = switch_method(current_method)

                    result = doTPCC(params, current_method)
                    if result == True:
                        temp_commit['after']['commit'] += 1
                    elif result == False:
                        temp_commit['after']['abort'] += 1

                # return to normal, don't execute Tx
                else:
                    next_check += check_interval
                    if temp_commit['after']['commit'] < temp_commit['before']['commit']:
                        current_method = switch_method(current_method)
                    else:
                        if current_method == "2pl":
                            print("{} {}: FRS -> 2PL".format(config.peer_name, current_time))
                        else:
                            print("{} {}: S2PL -> FRS".format(config.peer_name, current_time))

                    temp_changed_mode_flag = False
                    temp_commit = {'before': {'commit': 0, 'abort': 0}, 'after': {'commit': 0, 'abort': 0}}
                    continue

        # invalid method
        else:
            res_dic = {"result": "invalid method"}
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # get results
        res_dic = {}
        config.lock_management.get_result(display=True)
        res_dic1 = time_measurement.get_result(display=True)
        res_dic2 = config.time_measurement.get_result(display=True)
        res_dic.update(**res_dic1, **res_dic2)
        res_dic["basic_res"] = result_measurement.get_result(display=True)
        res_dic["process_time"] = timestamp_management.get_result(display=True)

        print("benchmark finished")
        return data_pb2.Response(json_str=json.dumps(res_dic))
