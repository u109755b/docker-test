import os
peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
import sys
sys.dont_write_bytecode = True
import json
import threading

# key: global_xid, value: Tx type object
tx_dict = {}

channels = {}
# channels_state = 0  # 0: initialized, 1: used, 2: finished
# channels_lock = threading.Lock()
# def clear_channels():
#     for channel in channels.values():
#         channel.close()
#     channels.clear()
# def channels_start():
#     with channels_state:
#         if channels_state != 1:
#             channels_state = 1
#             clear_channels()
# def channels_finish():
#     with channels_state:
#         if channels_state != 2:
#             channels_state = 2
#             clear_channels()

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



import time
import threading
class TimeMeasurement:
    def __init__(self):
        self.start_time = {}
        self.total_duration_time = {}
        self.data_num = {}
        self.status = 0     # 0: inited, 1: started, 2: ended

    def start(self):
        if self.status != 1:
            self.__init__()
            self.status = 1

    def finish(self):
        self.status = 2

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
        if time_type not in self.data_num:
            self.total_duration_time[time_type] = 0
            self.data_num[time_type] = 0
        self.total_duration_time[time_type] += e_time - s_time
        self.data_num[time_type] += 1

    def print_time(self):
        duration_time = []
        for time_type, td_time in self.total_duration_time.items():
            num = self.data_num[time_type]
            duration_time.append('{}: {:.2f}'.format(time_type, 1000*td_time/num))
            # duration_time[time_type] = td_time / self.data_num[time_type]
        print(', '.join(duration_time))
time_measurement = TimeMeasurement()


class ResultMeasurement:
    def __init__(self):
        # コミット数 (Updateコミット数+Readコミット数)  コミットの合計時間 (Updateコミットの合計時間+Readコミットの合計時間)
        # アボート数 (Globalアボート数+Localアボート数)  アボートの合計時間 (Globalアボートの合計時間+Localアボートの合計時間)
        self.update_commit_num = 0
        self.read_commit_num = 0
        self.update_commit_time = 0
        self.read_commit_time = 0
        
        self.global_abort_num = 0
        self.local_abort_num = 0
        self.global_abort_time = 0
        self.local_abort_time = 0
        
        self.start_time = 0
        
    def get_result(self, display=False):
        # provider3 |  commit: 8 (2 6)  6.20 (4.10 2.10)[s],   abort: 8 (4 4)  6.20 (4.07 2.13)[s]
        # commit
        commit_num = self.update_commit_num + self.read_commit_num
        commit_num_info = '{} ({} {})'.format(commit_num, self.update_commit_num, self.read_commit_num)
        commit_time = self.update_commit_time + self.read_commit_time
        commit_time_info = '{:.2f} ({:.2f} {:.2f})'.format(commit_time, self.update_commit_time, self.read_commit_time)
        commit_info = 'commit: {}  {}[s]'.format(commit_num_info, commit_time_info)
        # abort
        abort_num = self.global_abort_num + self.local_abort_num
        abort_num_info = '{} ({} {})'.format(abort_num, self.global_abort_num, self.local_abort_num)
        abort_time = self.global_abort_time + self.local_abort_time
        abort_time_info = '{:.2f} ({:.2f} {:.2f})'.format(abort_time, self.global_abort_time, self.local_abort_time)
        abort_info = 'abort: {}  {}[s]'.format(abort_num_info, abort_time_info)
        
        if display:
            print(commit_info)
            print(abort_info)
        return '{} |  {},   {}'.format(peer_name, commit_info, abort_info)
        
    def start_tx(self):
        self.start_time = time.perf_counter()
        
    def commit_tx(self, commit_type):
        commit_time = time.perf_counter() - self.start_time
        if commit_type == 'update':
            self.update_commit_num += 1
            self.update_commit_time += commit_time
        if commit_type == 'read':
            self.read_commit_num += 1
            self.read_commit_time += commit_time
            
    def abort_tx(self, abort_type):
        abort_time = time.perf_counter() - self.start_time
        if abort_type == 'global':
            self.global_abort_num += 1
            self.global_abort_time += abort_time
        if abort_type == 'local':
            self.local_abort_num += 1
            self.local_abort_time += abort_time
result_measurement = ResultMeasurement()