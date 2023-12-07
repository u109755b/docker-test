import os
peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
import sys
sys.dont_write_bytecode = True
import json
import time
import threading
import utils

# key: global_xid, value: Tx type object
tx_dict = {}

channels = {}

prelock_invalid = False
plock_mode = True
hop_mode = False
include_getting_tx_time = True
getting_tx = True

# sleep time
SLEEP_MS = 0

# config json
with open('dejima_config.json') as f:
    dejima_config_dict = json.load(f)

# prepare dt_list, bt_list
dt_list = [dt for dt in dejima_config_dict['dejima_table'].keys() if peer_name in dejima_config_dict['dejima_table'][dt]]
bt_list = dejima_config_dict['base_table'][peer_name]

# neighbor peers
neighbor_hop = 20
target_peers = {peer_name}
for i in range(neighbor_hop):
    next_target_peers = set()
    for peerlist_for_each_dt in dejima_config_dict["dejima_table"].values():
        peerset_for_each_dt = set(peerlist_for_each_dt)
        if target_peers & peerset_for_each_dt != set():
            next_target_peers = next_target_peers | peerset_for_each_dt
    target_peers = target_peers | next_target_peers
target_peers.remove(peer_name)




class TimingLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.wait_time_lock = threading.Lock()
        self.wait_time = 0

    def __enter__(self):
        start_time = time.perf_counter()
        self.lock.acquire()
        end_time = time.perf_counter()
        with self.wait_time_lock:
            self.wait_time += end_time - start_time
        # print(end_time-start_time)

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()


from itertools import product
class LockManagement:
    def init(self):
        self.plock = threading.Lock()
        self.tx_lock_list = {}

        self.locked = {}
        self.record_lock = {}
        for c_w_id, c_d_id, c_id in product(range(1, 101), range(1, 11), range(1, 101)):
            lineage = self.get_tpcc_lineage('customer', c_w_id, c_d_id, c_id)
            self.locked[lineage] = False
            self.record_lock[lineage] = TimingLock()

    def __init__(self):
        self.init()

    def get_tpcc_lineage(self, bt, c_w_id, c_d_id, c_id):
        peer_name = 'Peer{}'.format(10*(c_w_id-1) + c_d_id)
        record_id = '({})'.format(','.join([str(c_w_id), str(c_d_id), str(c_id)]))
        lineage = '{}-{}-{}'.format(peer_name, bt, record_id)
        return lineage

    def lock(self, global_xid, lineage):
        if global_xid not in self.tx_lock_list:
            self.tx_lock_list[global_xid] = []
        with self.record_lock[lineage]:
            if self.locked[lineage]:
                if lineage in self.tx_lock_list[global_xid]:
                    return
                else:
                    raise Exception('LockManagement: failed to lock a record')
            self.locked[lineage] = True
        self.tx_lock_list[global_xid].append(lineage)

    def unlock(self, global_xid):
        if global_xid not in self.tx_lock_list:
            return
        for lineage in self.tx_lock_list[global_xid]:
            with self.record_lock[lineage]:
                self.locked[lineage] = False
        del self.tx_lock_list[global_xid]

    def get_result(self, display=False):
        total_wait_time = 0
        with self.plock:
            for tx_lock in self.record_lock.values():
                total_wait_time += tx_lock.wait_time
        if display: print('total_wait_time: {}[ms]'.format(utils.round2(1000*total_wait_time)))
        return total_wait_time
lock_management = LockManagement()


class TimestampManagement:
    def __init__(self):
        self.duration_time = {'lock': 0, 'base_update': 0, 'prop_view_0': 0, 'view_update': 0, 'prop_view_k': 0, 'communication': 0, 'commit': 0}
        self.data_num = {'lock': 0, 'base_update': 0, 'prop_view_0': 0, 'view_update': 0, 'prop_view_k': 0, 'communication': 0, 'commit': 0}

    def add_duration_time(self, time_name, duration_time):
        self.duration_time[time_name] += duration_time
        self.data_num[time_name] += 1

    def add_timestamps(self, timestamps):
        timestamps = list(reversed(timestamps))
        self.add_duration_time("commit", timestamps[0][-1]-timestamps[0][-2])
        timestamps[0].pop()
        for i, timestamp in enumerate(timestamps):
            self.add_duration_time("lock", timestamp[1]-timestamp[0])
            if i == 0:
                self.add_duration_time('base_update', timestamp[2]-timestamp[1])
                self.add_duration_time('prop_view_0', timestamp[3]-timestamp[2])
            else:
                self.add_duration_time('view_update', timestamp[2]-timestamp[1])
                self.add_duration_time('prop_view_k', timestamp[3]-timestamp[2])
            if i != len(timestamps)-1:
                duration_time = (timestamps[i+1][0]-timestamps[i][-2]) + (timestamps[i][-1]-timestamps[i+1][-1])
                self.add_duration_time('communication', duration_time)

    def get_result(self, display=False):
        avg_ms = lambda x, y: utils.divide(1000*x, y)
        result = utils.general_2obj_func(self.duration_time, self.data_num, avg_ms)
        if display == True: print(utils.general_round2(result), end='[ms]\n')
        return result


class TimeMeasurement:
    def init(self):
        self.start_time = {}
        self.total_duration_time = {}
        self.data_num = {}
        self.plock = threading.Lock()

    def __init__(self):
        self.init()

    def start_timer(self, time_type, global_xid, s_time=None):
        if time_type not in self.start_time:
            self.start_time[time_type] = {}
        if global_xid not in self.start_time[time_type]:
            self.start_time[time_type][global_xid] = []
        if s_time is None:
            s_time = time.perf_counter()
        self.start_time[time_type][global_xid].append(s_time)

    def stop_timer(self, time_type, global_xid, save=True):
        s_time = self.start_time[time_type][global_xid].pop()
        e_time = time.perf_counter()
        if not self.start_time[time_type][global_xid]:
            del self.start_time[time_type][global_xid]
        if save is False:
            return
        if time_type not in self.total_duration_time:
            self.total_duration_time[time_type] = []
            self.data_num[time_type] = []
        self.total_duration_time[time_type].append(e_time - s_time)
        self.data_num[time_type].append(1)

    def get_result(self, display=False):
        result = {}
        with self.plock:
            for time_type, td_time in self.total_duration_time.items():
                total_time = sum(self.total_duration_time[time_type])
                total_num = sum(self.data_num[time_type])
                self.total_duration_time[time_type] = [total_time]
                self.data_num[time_type] = [total_num]
                if time_type == 'lock_process': result[time_type] = 1000*total_time
                else: result[time_type] = 1000*total_time / total_num
        if not result: return {}
        if display == True: print(utils.general_round2(result), end='[ms]\n')
        return result
time_measurement = TimeMeasurement()


class ResultMeasurement:
    def __init__(self):
        # コミット数 (Updateコミット数+Readコミット数)  コミットの合計時間 (Updateコミットの合計時間+Readコミットの合計時間)
        # アボート数 (Globalアボート数+Localアボート数)  アボートの合計時間 (Globalアボートの合計時間+Localアボートの合計時間)
        self.start_time = 0
        
        self.update_commit_num = 0
        self.read_commit_num = 0
        self.update_commit_time = 0
        self.read_commit_time = 0
        self.commit_hop = 0
        
        self.global_abort_num = 0
        self.local_abort_num = 0
        self.global_abort_time = 0
        self.local_abort_time = 0
        self.abort_hop = 0
        
        self.global_lock_start_time = 0
        self.global_lock_time = 0
        self.total_global_lock_time = 0
        
    def get_result(self, display=False):
        # commit: 8 (2 6)  6.20 (4.10 2.10)[s],   abort: 8 (4 4)  6.20 (4.07 2.13)[s]
        # commit
        commit_num = self.update_commit_num + self.read_commit_num
        commit_time = self.update_commit_time + self.read_commit_time
        commit_hop = utils.divide(self.commit_hop, self.update_commit_num)
        # abort
        abort_num = self.global_abort_num + self.local_abort_num
        abort_time = self.global_abort_time + self.local_abort_time
        abort_hop = utils.divide(self.abort_hop, self.global_abort_num)
        
        result = {
            "commit": [commit_num,  self.update_commit_num,  self.read_commit_num],
            "abort": [abort_num,  self.global_abort_num,  self.local_abort_num],
            "commit_time": [commit_time,  self.update_commit_time,  self.read_commit_time],
            "abort_time": [abort_time,  self.global_abort_time,  self.local_abort_time],
            "custom_commit": [self.update_commit_num*commit_hop,  self.update_commit_num,  commit_hop],
            "custom_abort": [self.global_abort_num*abort_hop,  self.global_abort_num,  abort_hop],
            "global_lock": [self.total_global_lock_time],
        }
        
        if display:
            rounded_result = utils.general_1obj_func(result, utils.round2)
            # commit
            print("commit: {} ({} {})".format(*rounded_result["commit"]), end="  ")
            print("{} ({} {})[s]".format(*rounded_result["commit_time"]), end=",   ")
            print("{} = {} * {}".format(*rounded_result["custom_commit"]))
            # abort
            print("abort: {} ({} {})".format(*rounded_result["abort"]), end="  ")
            print("{} ({} {})[s]".format(*rounded_result["abort_time"]), end=",   ")
            print("{} = {} * {}".format(*rounded_result["custom_abort"]))
            # global lock
            print("global lock: {}[s]".format(*rounded_result["global_lock"]))
        return result
        
    def start_tx(self):
        self.start_time = time.perf_counter()
        
    def start_global_lock(self):
        self.global_lock_start_time = time.perf_counter()
        
    def finish_global_lock(self):
        self.global_lock_time = time.perf_counter() - self.global_lock_start_time
        
    def commit_tx(self, commit_type, hop=1):
        commit_time = time.perf_counter() - self.start_time
        if commit_type == 'update':
            self.update_commit_num += 1
            self.update_commit_time += commit_time
            self.commit_hop += hop
            self.total_global_lock_time += self.global_lock_time
        if commit_type == 'read':
            self.read_commit_num += 1
            self.read_commit_time += commit_time
            
    def abort_tx(self, abort_type, hop=1):
        abort_time = time.perf_counter() - self.start_time
        if abort_type == 'global':
            self.global_abort_num += 1
            self.global_abort_time += abort_time
            self.abort_hop += hop
        if abort_type == 'local':
            self.local_abort_num += 1
            self.local_abort_time += abort_time