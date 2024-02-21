import os
import sys
import json

peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
sys.dont_write_bytecode = True

# key: global_xid, value: Tx type object
tx_dict = {}
pid_to_tx = {}
prop_visited = {}

channels = {}

trace_enabled = False
host_name = 'host.docker.internal'   # ローカル環境のとき
# host_name = requests.get('https://ifconfig.me').text   # AWS EC2など他の環境の時

prelock_request_invalid = False
prelock_invalid = False
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
