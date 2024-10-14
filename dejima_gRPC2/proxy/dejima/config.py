import os
import sys
import json
import math
from collections import deque
from collections import defaultdict

peer_name = os.environ['PEER_NAME'] # peer_name must be calculated at first
sys.dont_write_bytecode = True

# key: global_xid, value: Tx type object
tx_dict = {}
pid_to_tx = {}
prop_visited = {}

channels = {}
tx_type_count = defaultdict(int)

trace_enabled = False
host_name = 'host.docker.internal'   # ローカル環境のとき
# host_name = requests.get('https://ifconfig.me').text   # AWS EC2など他の環境の時

prelock_request_invalid = False
prelock_invalid = False
hop_mode = True
include_getting_tx_time = True
getting_tx = True
adr_mode = True
use_prop_weights = True
termination_method = "all"   # "neighbor" or "all"

# # straight 5
# adr_peers = ["Peer3"]
# adr_peers = ["Peer2", "Peer3"]
# adr_peers = ["Peer2", "Peer3", "Peer4"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5"]

# # straight 9
# adr_peers = ["Peer5"]
# adr_peers = ["Peer4", "Peer5", "Peer6"]
adr_peers = ["Peer3", "Peer4", "Peer5", "Peer6", "Peer7"]
# adr_peers = ["Peer2", "Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8", "Peer9"]

# # straight 10
# adr_peers = ["Peer5"]
# adr_peers = ["Peer5", "Peer6"]
# adr_peers = ["Peer4", "Peer5", "Peer6", "Peer7"]
# adr_peers = ["Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8"]
# adr_peers = ["Peer2", "Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8", "Peer9"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8", "Peer9", "Peer10"]

# # star2 10
# adr_peers = ["Peer1"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8", "Peer9", "Peer10"]

# sleep time
SLEEP_MS = 0

# config json
with open('dejima_config.json') as f:
    dejima_config_dict = json.load(f)

# prepare dt_list, bt_list
dt_list = [dt for dt in dejima_config_dict['dejima_table'].keys() if peer_name in dejima_config_dict['dejima_table'][dt]]
bt_list = dejima_config_dict['base_table'][peer_name]
bt_list_all = list(set(sum(bt_list.values(), [])))

def get_neighbor_peers(peer):
    peer_set = set()
    for peerlist_for_each_dt in dejima_config_dict["dejima_table"].values():
        peerset_for_each_dt = set(peerlist_for_each_dt)
        if peer in peerset_for_each_dt:
            peer_set |= peerset_for_each_dt
    peer_set.remove(peer)
    return peer_set

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

neighbor_peers = get_neighbor_peers(peer_name)
