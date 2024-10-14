import math
import random
import os
from collections import deque
from collections import defaultdict
from dejima import config


prop_log_limit = 30

def get_stable_average(original_list, remove_num):
    if not original_list: return 0
    if len(original_list) <= 2*remove_num: return sum(original_list) / len(original_list)
    if remove_num:
        filterd_list = sorted(original_list)[remove_num:-remove_num]
    else:
        filterd_list = original_list
    return sum(filterd_list) / len(filterd_list)

# lock_time = 0
# base_update_time = 0
# prop_view_time = 0
# total_update_prop_time = 0
lock_time = deque(maxlen=prop_log_limit)
base_update_time = deque(maxlen=prop_log_limit)
prop_view_time = deque(maxlen=prop_log_limit)
total_update_prop_time = deque(maxlen=prop_log_limit)
update_cnt_all = 0

def add_update_prop_time(_lock_time, _base_update_time, _prop_view_time, _total):
    global lock_time, base_update_time, prop_view_time, total_update_prop_time
    global update_cnt_all
    # lock_time += _lock_time
    # base_update_time += _base_update_time
    # prop_view_time += _prop_view_time
    # total_update_prop_time += _total
    lock_time.append(_lock_time)
    base_update_time.append(_base_update_time)
    prop_view_time.append(_prop_view_time)
    total_update_prop_time.append(_total)
    update_cnt_all += 1

def get_update_prop_time():
    # if update_cnt_all == 0: return 0, 0, 0, 0
    # update_cnt_recent = len(total_update_prop_time)
    # return sum(lock_time) / update_cnt_recent,\
    #         sum(base_update_time) / update_cnt_recent,\
    #         sum(prop_view_time) / update_cnt_recent,\
    #         sum(total_update_prop_time) / update_cnt_recent
    return get_stable_average(lock_time, 2),\
           get_stable_average(base_update_time, 2),\
           get_stable_average(prop_view_time, 2),\
           get_stable_average(total_update_prop_time, 2)


# total_read_prop_time = 0
total_read_prop_time = deque(maxlen=prop_log_limit)
read_cnt_all = 0

def add_read_prop_time(prop_time):
    global total_read_prop_time
    global read_cnt_all
    # total_read_prop_time += prop_time
    total_read_prop_time.append(prop_time)
    read_cnt_all += 1

def get_read_prop_time():
    # if read_cnt_all == 0: return 0
    # read_cnt_recent = len(total_read_prop_time)
    # return sum(total_read_prop_time) / read_cnt_recent
    return get_stable_average(total_read_prop_time, 2)


# total_commit_prop_time = 0
total_commit_prop_time = deque(maxlen=prop_log_limit)
commit_cnt_all = 0

def add_commit_prop_time(prop_time):
    global total_commit_prop_time
    global commit_cnt_all
    # total_commit_prop_time += prop_time
    total_commit_prop_time.append(prop_time)
    commit_cnt_all += 1

def get_commit_prop_time():
    # if commit_cnt_all == 0: return 0
    # commit_cnt_recent = len(total_commit_prop_time)
    # return sum(total_commit_prop_time) / commit_cnt_recent
    return get_stable_average(total_commit_prop_time, 2)



original_r_direction = {}
visit_queue = deque(config.adr_peers)
visited = set(config.adr_peers)
while visit_queue:
    cur_peer = visit_queue.popleft()
    for next_peer in config.get_neighbor_peers(cur_peer):
        if next_peer in visited: continue
        visit_queue.append(next_peer)
        visited.add(next_peer)
        original_r_direction[next_peer] = cur_peer



is_r_peer = {}
is_edge_r_peer = {}
r_direction = {}
request_count = defaultdict(deque)

def init_adr_setting(lineage):
    # is_r_peer
    is_r_peer[lineage] = (config.peer_name in config.adr_peers)
    # r_direction
    if config.peer_name in config.adr_peers:
        r_direction[lineage] = set()
        for peer in config.neighbor_peers:
            if peer not in config.adr_peers: continue
            r_direction[lineage].add(peer)
    else:
        r_direction[lineage] = set([original_r_direction[config.peer_name]])
    # is_edge_r_peer
    if is_r_peer[lineage] and len(r_direction[lineage]) <= 1:
        is_edge_r_peer[lineage] = True
    else:
        is_edge_r_peer[lineage] = False

def init_adr_setting_if_not(lineages):
    if type(lineages) is str:
        lineages = [lineages]
    for lineage in set(lineages):
        if lineage not in is_r_peer:
            init_adr_setting(lineage)
    return lineages

def get_is_r_peer(lineage):
    init_adr_setting_if_not(lineage)
    return is_r_peer[lineage]

def get_is_edge_r_peer(lineage):
    init_adr_setting_if_not(lineage)
    return is_edge_r_peer[lineage]

def get_r_direction(lineage):
    init_adr_setting_if_not(lineage)
    return r_direction[lineage]



# expansion contraction manager
class ECManager:
    def __init__(self):
        self.default_log_look_range = 7
        self.log = []

    def add_log(self, test_type, parent_peer):
        if test_type != "expansion" and test_type != "contraction":
            raise TypeError("test_type must be 'expansion' or 'contraction'")
        self.log.append((test_type, parent_peer))

    def get_test_type(self, request_type):
        if request_type == "read": return "expansion"
        elif request_type == "update": return "contraction"
        else: raise TypeError("request_type must be 'read' or 'update'")

    def get_ec_num(self, test_type, peer):
        return sum(log == (test_type, peer) for log in self.log)

    def get_probability(self, test_type):
        if len(self.log) <= 10: return 0.5
        p = sum(log[0] == test_type for log in self.log) / len(self.log)
        return p

    def get_entropy(self):
        p = self.get_probability("expansion")
        q = 1-p
        if math.isclose(p, 0) or math.isclose(p, 1.0):
            return 0
        entropy = -p*math.log2(p) - q*math.log2(q)
        return entropy

    def get_probability_2peer(self, test_type, peer, ec_num):
        log_num = sum(log == (test_type, peer) for log in self.log)
        if log_num + ec_num <= 10: return 0.5
        p = log_num / (log_num + ec_num)
        return p

    def get_entropy_2peer(self, test_type, peer, ec_num):
        p = self.get_probability_2peer(test_type, peer, ec_num)
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
        if log_look_range <= 5:
            log_look_range = 5
        return log_look_range

    def get_log_look_range_2peer(self, request_type, peer, ec_num):
        test_type = self.get_test_type(request_type)
        entropy = self.get_entropy_2peer(test_type, peer, ec_num)
        if self.get_probability_2peer(test_type, peer, ec_num) < 0.5:
            entropy = 1.0
        log_look_range = round(self.default_log_look_range * entropy)
        if log_look_range <= 5:
            log_look_range = 5
        return log_look_range

ec_manager = ECManager()



def countup_request(lineages, request_type, parent_peer):
    lineages = init_adr_setting_if_not(lineages)
    for lineage in set(lineages):
        if not get_is_edge_r_peer(lineage): continue
        request_count[lineage].appendleft((request_type, parent_peer))
        if len(request_count[lineage]) > ec_manager.default_log_look_range + 1000:
            request_count[lineage].pop()



def ec_test(lineages, request_type, parent_peer, ec_num):
    if parent_peer == config.peer_name: return []
    lineages = init_adr_setting_if_not(lineages)
    res_lineages = []
    for lineage in set(lineages):
        if not get_is_edge_r_peer(lineage): continue
        update_count = 0
        read_count = 0
        log_look_range = ec_manager.get_log_look_range_2peer(request_type, parent_peer, ec_num)
        if len(request_count[lineage]) < log_look_range: continue
        is_ec = False
        # expansion test
        if request_type == "read" and parent_peer not in get_r_direction(lineage):
            for req in request_count[lineage]:
                if req[0] == "update" and req[1] != parent_peer: update_count += 1
                if req[0] == "read" and req[1] == parent_peer: read_count += 1
                if update_count + read_count >= log_look_range: break
            if update_count + read_count < log_look_range: continue
            if config.use_prop_weights and update_cnt_all > 10 and read_cnt_all > 10:
                if update_count * get_update_prop_time()[3] - read_count * get_read_prop_time() < 0:
                    is_ec = True
            else:
                if update_count - read_count < 0:
                    is_ec = True
        # contraction test
        if request_type == "update" and parent_peer in get_r_direction(lineage):
            for req in request_count[lineage]:
                if req[0] == "update" and req[1] == parent_peer: update_count += 1
                if req[0] == "read" and req[1] != parent_peer: read_count += 1
                if update_count + read_count >= log_look_range: break
            if update_count + read_count < log_look_range: continue
            if config.use_prop_weights and update_cnt_all > 10 and read_cnt_all > 10:
                if read_count * get_read_prop_time() - update_count * get_update_prop_time()[3] < 0:
                    is_ec = True
            else:
                if read_count - update_count < 0:
                    is_ec = True
        if is_ec: res_lineages.append(lineage)
    # return []
    return res_lineages

def get_expansion_lineages(lineages, parent_peer, contraction_num):
    return ec_test(lineages, "read", parent_peer, contraction_num)

def get_contraction_lineages(lineages, parent_peer, expansion_num):
    return ec_test(lineages, "update", parent_peer, expansion_num)



def expansion_old(lineages, parent_peer):
    for lineage in lineages:
        r_direction[lineage].add(parent_peer)
        request_count[lineage] = deque()
        is_edge_r_peer[lineage] = (len(r_direction[lineage]) <= 1)
        ec_manager.add_log("expansion", parent_peer)

def expansion_new(lineages, r_direction_peer):
    for lineage in lineages:
        is_r_peer[lineage] = True
        is_edge_r_peer[lineage] = True
        r_direction[lineage] = set([r_direction_peer])
        request_count[lineage] = deque()

def contraction_old(lineages, parent_peer):
    for lineage in lineages:
        is_r_peer[lineage] = False
        is_edge_r_peer[lineage] = False
        request_count[lineage] = deque()
        ec_manager.add_log("contraction", parent_peer)

def contraction_new(lineages, non_r_peer):
    for lineage in lineages:
        r_direction[lineage].remove(non_r_peer)
        is_edge_r_peer[lineage] = (len(r_direction[lineage]) <= 1)
        request_count[lineage] = deque()
