import os
peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
import sys
sys.dont_write_bytecode = True
import json

# key: global_xid, value: Tx type object
tx_dict = {}

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