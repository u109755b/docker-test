import time
import config
import random
from frs.do_rsab_provider_tx import doRSAB_PROVIDER_frs
from two_pl.do_rsab_provider_tx import doRSAB_PROVIDER_2pl

class RSABProvider(object):
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
        switch_cnt = []
        result_per_epoch = [{'commit': 0, 'abort': 0}]
        commit_abort_miss = {}
        commit_abort_miss['transaction'] = {'commit': 0, 'abort': 0, 'miss': 0}
        # commit_abort_miss['detect_update'] = {'commit': 0, 'abort': 0, 'miss': 0}
        epoch = 0
        epoch_time = 100
        next_epoch_start_time = epoch_time
        start_time = time.time()
        print("benchmark start")
        random.seed()
        
        total_commit_time = 0
        total_abort_time = 0

        # frs & 2pl
        if METHOD == "frs" or METHOD == "2pl":
            if METHOD == "frs":
                doRSAB = doRSAB_PROVIDER_frs
            else:
                doRSAB = doRSAB_PROVIDER_2pl
            config.timestamp_management = config.TimestampManagement()
            
            current_time = time.time() - start_time
            while (current_time < bench_time):
                current_time = time.time() - start_time
                # epoch update
                if current_time > next_epoch_start_time:
                    next_epoch_start_time += epoch_time
                    epoch += 1
                    result_per_epoch.append({'commit': 0, 'abort': 0})
                
                start_doRSAB = time.perf_counter()
                result = doRSAB()
                end_doRSAB = time.perf_counter()
                t_type = 'transaction'
                if result == True:
                    commit_num += 1
                    result_per_epoch[epoch]['commit'] += 1
                    commit_abort_miss[t_type]['commit'] += 1
                    total_commit_time += end_doRSAB-start_doRSAB
                elif result == False:
                    abort_num += 1
                    result_per_epoch[epoch]['abort'] += 1
                    commit_abort_miss[t_type]['abort'] += 1
                    total_abort_time += end_doRSAB-start_doRSAB
                elif result == "miss":
                    miss_num += 1
                    miss_time += time.time() - start_time - current_time
                    commit_abort_miss[t_type]['miss'] += 1
            print(config.timestamp_management.get_result())
                
                # time.sleep(0.1)

        # hybrid
        elif METHOD == "hybrid":
            current_method = "2pl"
            doRSAB = doRSAB_PROVIDER_2pl
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
                # normal mode
                if current_time < next_check:
                    result = doRSAB()
                    if result == True:
                        commit_num += 1
                    elif result == False:
                        abort_num += 1
                    elif result == "miss":
                        miss_num += 1

                # check mode
                # before
                elif current_time < next_check + check_time:
                    result = doRSAB()
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
                            doRSAB = doRSAB_PROVIDER_frs
                        else:
                            current_method = "2pl"
                            doRSAB = doRSAB_PROVIDER_2pl

                    result = doRSAB()
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
                        switch_cnt.append(0)
                        if current_method == "2pl":
                            current_method = "frs"
                            doRSAB = doRSAB_PROVIDER_frs
                        else:
                            current_method = "2pl"
                            doRSAB = doRSAB_PROVIDER_2pl
                    else:
                        switch_cnt.append(1)
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
        
        # transaction_result = []
        # for cam_str in ['commit', 'abort', 'miss']:
        #     transaction_result.append(str(commit_abort_miss['transaction'][cam_str]))
        # transaction_result = " ".join(transaction_result)
        
        msg = " ".join([config.peer_name, str(commit_num), str(abort_num), str(miss_num), str(bench_time-miss_time)])
        print("total commit time: {}, total abort time: {}".format(total_commit_time, total_abort_time))
        # msg = config.peer_name + ":  " + transaction_result + ",  " + str(bench_time-miss_time)
        
        if switch_cnt != []:
            msg += " *" + " ".join(map(str, switch_cnt)) + "*"
        # for result in result_per_epoch:
        #     msg += " " + str(result['commit'])
        # for result in result_per_epoch:
        #     msg += " " + str(result['abort'])
        msg += "\n"

        print("benchmark finished")
        resp.text = msg
        return
