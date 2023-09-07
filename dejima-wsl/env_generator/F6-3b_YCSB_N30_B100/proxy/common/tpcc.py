import time
import config
import random
from frs.do_tpcc_no_tx import doTPCC_NO_frs
from frs.do_tpcc_pay_tx import doTPCC_PAY_frs
from two_pl.do_tpcc_no_tx import doTPCC_NO_2pl
from two_pl.do_tpcc_pay_tx import doTPCC_PAY_2pl

class TPCC(object):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        # get params
        params = req.params
        param_keys = ["bench_time", "method"]
        for key in param_keys:
            if not key in params.keys():
                msg = "Invalid parameters"
                resp.text = msg
                return
        bench_time = int(params['bench_time'])
        METHOD = params['method']
            
        # benchmark
        commit_num = 0
        abort_num = 0
        miss_num = 0
        miss_time = 0
        result_per_epoch = [{'commit': 0, 'abort': 0}]
        epoch = 0
        epoch_time = 100
        next_epoch_start_time = epoch_time
        start_time = time.time()
        print("benchmark start")
        random.seed()

        # frs & 2pl
        if METHOD == "frs" or METHOD == "2pl":
            if METHOD == "frs":
                doTPCC_NO = doTPCC_NO_frs
                doTPCC_PAY = doTPCC_PAY_frs
            else:
                doTPCC_NO = doTPCC_NO_2pl
                doTPCC_PAY = doTPCC_PAY_2pl

            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time
                # epoch update
                if current_time > next_epoch_start_time:
                    next_epoch_start_time += epoch_time
                    epoch += 1
                    result_per_epoch.append({'commit': 0, 'abort': 0})

                if random.randint(1,100) < 50:
                    doTPCC = doTPCC_NO
                else:
                    doTPCC = doTPCC_PAY
                result = doTPCC()
                if result == True:
                    commit_num += 1
                    result_per_epoch[epoch]['commit'] += 1
                elif result == False:
                    result_per_epoch[epoch]['abort'] += 1
                    abort_num += 1
                elif result == "miss":
                    miss_num += 1
                    miss_time += time.time() - start_time - current_time

        # hybrid
        elif METHOD == "hybrid":
            current_method = "2pl"
            doTPCC_NO = doTPCC_NO_2pl
            doTPCC_PAY = doTPCC_PAY_2pl
            check_time = 30
            check_interval = 300
            # determine first check timing
            next_check = random.randint(0,check_interval - check_time * 2)

            temp_commit = {'before': {'commit': 0, 'abort': 0}, 'after': {'commit': 0, 'abort': 0}}
            temp_changed_mode_flag = False

            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time

                # epoch update
                if current_time > next_epoch_start_time:
                    next_epoch_start_time += epoch_time
                    epoch += 1
                    result_per_epoch.append({'commit': 0, 'abort': 0})

                if random.randint(1,100) < 50:
                    doTPCC = doTPCC_NO
                else:
                    doTPCC = doTPCC_PAY

                # normal mode
                if current_time < next_check:
                    result = doTPCC()
                    if result == True:
                        commit_num += 1
                    elif result == False:
                        abort_num += 1
                    elif result == "miss":
                        miss_num += 1

                # check mode
                # before
                elif current_time < next_check + check_time:
                    result = doTPCC()
                    if result == True:
                        temp_commit['before']['commit'] += 1
                        commit_num += 1
                    elif result == False:
                        temp_commit['before']['abort'] += 1
                        abort_num += 1
                    elif result == "miss":
                        miss_num += 1
                # after
                elif current_time < next_check + check_time * 2:
                    # change method if this is first time
                    if not temp_changed_mode_flag:
                        temp_changed_mode_flag = True
                        if current_method == "2pl":
                            current_method = "frs"
                            doTPCC_NO = doTPCC_NO_frs
                            doTPCC_PAY = doTPCC_PAY_frs
                        else:
                            current_method = "2pl"
                            doTPCC_NO = doTPCC_NO_2pl
                            doTPCC_PAY = doTPCC_PAY_2pl

                    result = doTPCC()
                    if result == True:
                        temp_commit['after']['commit'] += 1
                        commit_num += 1
                    elif result == False:
                        temp_commit['after']['abort'] += 1
                        abort_num += 1
                    elif result == "miss":
                        miss_num += 1

                # return to normal, don't execute Tx
                else:
                    next_check += check_interval
                    if temp_commit['after']['commit'] < temp_commit['before']['commit']:
                        if current_method == "2pl":
                            current_method = "frs"
                            doTPCC_NO = doTPCC_NO_frs
                            doTPCC_PAY = doTPCC_PAY_frs
                        else:
                            current_method = "2pl"
                            doTPCC_NO = doTPCC_NO_2pl
                            doTPCC_PAY = doTPCC_PAY_2pl
                    else:
                        if current_method == "2pl":
                            print("{} {}: FRS -> 2PL".format(config.peer_name, current_time))
                        else:
                            print("{} {}: S2PL -> FRS".format(config.peer_name, current_time))

                    temp_changed_mode_flag = False
                    temp_commit = {'before': {'commit': 0, 'abort': 0}, 'after': {'commit': 0, 'abort': 0}}
                    continue

                if result == True:
                    result_per_epoch[epoch]['commit'] += 1
                elif result == False:
                    result_per_epoch[epoch]['abort'] += 1
                elif result == "miss":
                    miss_time += time.time() - start_time - current_time

        # invalid method
        else:
            resp.text = "invalid method"
            return

        msg = " ".join([config.peer_name, str(commit_num), str(abort_num), str(miss_num), str(bench_time-miss_time)])
        for result in result_per_epoch:
            msg += " " + str(result['commit'])
        for result in result_per_epoch:
            msg += " " + str(result['abort'])
        msg += "\n"

        print("benchmark finished")
        resp.text = msg
        return
