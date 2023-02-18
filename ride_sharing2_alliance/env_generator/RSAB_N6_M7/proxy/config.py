import os
peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
import sys
sys.dont_write_bytecode = True
import json

# key: global_xid, value: Tx type object
tx_dict = {}

# candidate_record_ids = set()
candidate_record_id_list = []

# sleep time
SLEEP_MS = 0

# config json
with open('dejima_config.json') as f:
    dejima_config_dict = json.load(f)

# prepare dt_list, bt_list
dt_list = [dt for dt in dejima_config_dict['dejima_table'].keys() if peer_name in dejima_config_dict['dejima_table'][dt]]
bt_list = dejima_config_dict['base_table'][peer_name]
if peer_name[0] == 'p':
    sorted_al_list = sorted(dejima_config_dict['alliance_list'][peer_name])

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


class TimestampManagement:
    def __init__(self):
        self.duration_time = {'get_xid': 0, 'lock': 0, 'base_update': 0, 'view_udpate': 0, 'prop_view': 0, 'communication': 0}
        self.data_num = {'get_xid': 0, 'lock': 0, 'base_update': 0, 'view_udpate': 0, 'prop_view': 0, 'communication': 0}
        
    def print_timestamps(self, timestamps):
        res = []
        for timestamp in timestamps:
            # short_format = map(lambda time: '{:.2f}'.format(time), timestamp)
            short_format = map(lambda time: float('{:.2f}'.format(time)), timestamp)
            res.append(list(short_format))
        print(res)
        
    def add_duration_time(self, time_name, duration_time):
        self.duration_time[time_name] += duration_time
        self.data_num[time_name] += 1
    
    def add_timestamps(self, timestamps):
        timestamps = list(reversed(timestamps))
        # self.print_timestamps(timestamps)
        for i, timestamp in enumerate(timestamps):
            self.add_duration_time('get_xid', (timestamp[1]-timestamp[0]) + timestamp[4]-timestamp[3])
            self.add_duration_time('lock', timestamp[2]-timestamp[1])
            if i == 0:
                self.add_duration_time('base_update', timestamp[3]-timestamp[2])
            else:
                self.add_duration_time('view_udpate', timestamp[3]-timestamp[2])
            self.add_duration_time('prop_view', timestamp[5]-timestamp[4])
            if i != len(timestamps)-1:
                duration_time = (timestamps[i+1][0]-timestamps[i][5]) + timestamps[i][-1]-timestamps[i+1][-1]
                self.add_duration_time('communication', duration_time)
    
    def get_result(self):
        result = {'get_xid': 0, 'lock': 0, 'base_update': 0, 'view_udpate': 0, 'prop_view': 0, 'communication': 0}
        for key in self.duration_time:
            time = self.duration_time[key] / self.data_num[key]
            result[key] = float('{:.2f}'.format(time))
        return result
timestamp_management = TimestampManagement()