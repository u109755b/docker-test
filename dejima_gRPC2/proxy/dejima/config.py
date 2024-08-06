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

trace_enabled = False
host_name = 'host.docker.internal'   # ローカル環境のとき
# host_name = requests.get('https://ifconfig.me').text   # AWS EC2など他の環境の時

prelock_request_invalid = False
prelock_invalid = False
hop_mode = False
include_getting_tx_time = True
getting_tx = True
adr_mode = True

# # straight 5
# adr_peers = ["Peer3"]
# adr_peers = ["Peer2", "Peer3"]
# adr_peers = ["Peer2", "Peer3", "Peer4"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4"]
# adr_peers = ["Peer1", "Peer2", "Peer3", "Peer4", "Peer5"]

# # straight 10
# adr_peers = ["Peer5"]
# adr_peers = ["Peer5", "Peer6"]
# adr_peers = ["Peer4", "Peer5", "Peer6", "Peer7"]
adr_peers = ["Peer3", "Peer4", "Peer5", "Peer6", "Peer7", "Peer8"]
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


# adr setting
original_r_direction = {}
visit_queue = deque(adr_peers)
visited = set(adr_peers)
while visit_queue:
    cur_peer = visit_queue.popleft()
    for next_peer in get_neighbor_peers(cur_peer):
        if next_peer in visited: continue
        visit_queue.append(next_peer)
        visited.add(next_peer)
        original_r_direction[next_peer] = cur_peer

is_r_peer = {}
is_edge_r_peer = {}
r_direction = {}

def init_adr_setting(lineage):
    # is_r_peer
    is_r_peer[lineage] = (peer_name in adr_peers)
    # r_direction
    if peer_name in adr_peers:
        r_direction[lineage] = set()
        for peer in neighbor_peers:
            if peer not in adr_peers: continue
            r_direction[lineage].add(peer)
    else:
        r_direction[lineage] = set([original_r_direction[peer_name]])
    # is_edge_r_peer
    if is_r_peer[lineage] and len(r_direction[lineage]) <= 1:
        is_edge_r_peer[lineage] = True
    else:
        is_edge_r_peer[lineage] = False

def get_is_r_peer(lineage):
    if lineage not in is_r_peer:
        init_adr_setting(lineage)
    return is_r_peer[lineage]

def get_is_edge_r_peer(lineage):
    if lineage not in is_edge_r_peer:
        init_adr_setting(lineage)
    return is_edge_r_peer[lineage]

def get_r_direction(lineage):
    if lineage not in r_direction:
        init_adr_setting(lineage)
    return r_direction[lineage]

request_count = defaultdict(deque)

# expansion contraction manager
class ECManager:
    def __init__(self):
        self.default_log_look_range = 3
        self.log = []

    def add_log(self, test_type):
        if test_type != "expansion" and test_type != "contraction":
            raise TypeError("test_type must be 'expansion' or 'contraction'")
        self.log.append(test_type)

    def get_test_type(self, request_type):
        if request_type == "read": return "expansion"
        elif request_type == "update": return "contraction"
        else: raise TypeError("request_type must be 'read' or 'update'")

    def get_probability(self, test_type):
        if len(self.log) <= 10: return 0.5
        p = sum(log == test_type for log in self.log) / len(self.log)
        return p

    def get_entropy(self):
        p = self.get_probability("expansion")
        q = 1-p
        if math.isclose(p, 0) or math.isclose(p, 1.0):
            return 0
        entropy = -p*math.log2(p) - q*math.log2(q)
        return entropy

    def get_log_look_range(self, request_type):
        test_type = self.get_test_type(request_type)
        entropy = self.get_entropy()
        if self.get_probability(test_type) < 0.5:
            entropy = 1.0
        log_look_range = round(self.default_log_look_range * entropy)
        if log_look_range == 0:
            log_look_range = 1
        return log_look_range

ec_manager = ECManager()

def countup_request(lineages, request_type, parent_peer):
    expansion_lineages = []
    contraction_lineages = []
    if type(lineages) is str:
        lineages = [lineages]
    for lineage in set(lineages):
        if lineage not in is_r_peer:
            init_adr_setting(lineage)
        if not get_is_edge_r_peer(lineage): continue
        request_count[lineage].appendleft((request_type, parent_peer))
        log_look_range = ec_manager.get_log_look_range(request_type)
        if parent_peer == peer_name: continue
        # expansion test
        if request_type == "read" and parent_peer not in get_r_direction(lineage):
            update_count = 0
            read_count = 0
            for _, req in zip(range(log_look_range), request_count[lineage]):
                if req[0] == "update" and req[1] != parent_peer: update_count += 1
                if req[0] == "read" and req[1] == parent_peer: read_count += 1
            if read_count > update_count:
                expansion_lineages.append(lineage)
                ec_manager.add_log("expansion")
            # print(f"read {lineage}: {read_count} {update_count} {request_count[lineage]}")
        # contraction test
        if request_type == "update" and parent_peer in get_r_direction(lineage):
            if parent_peer not in get_r_direction(lineage): continue
            update_count = 0
            read_count = 0
            for _, req in zip(range(log_look_range), request_count[lineage]):
                if req[0] == "update" and req[1] == parent_peer: update_count += 1
                if req[0] == "read" and req[1] != parent_peer: read_count += 1
            if read_count < update_count:
                contraction_lineages.append(lineage)
                ec_manager.add_log("contraction")
            # print(f"update {lineage}: {read_count} {update_count} {request_count[lineage]}")
    # return []
    if not expansion_lineages and not contraction_lineages: return []
    if expansion_lineages: return expansion_lineages
    if contraction_lineages: return contraction_lineages
