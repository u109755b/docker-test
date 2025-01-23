import math
import random
import os
import heapq
import copy
from collections import deque
from collections import defaultdict
from dejima import config


prop_log_limit = 30

# get_stable_average
def get_stable_average(original_list, remove_num):
    if not original_list: return 0
    if len(original_list) <= 2*remove_num: return sum(original_list) / len(original_list)
    if remove_num:
        filterd_list = sorted(original_list)[remove_num:-remove_num]
    else:
        filterd_list = original_list
    return sum(filterd_list) / len(filterd_list)


# update_prop_time
lock_time = deque(maxlen=prop_log_limit)
base_update_time = deque(maxlen=prop_log_limit)
prop_view_time = deque(maxlen=prop_log_limit)
total_update_prop_time = deque(maxlen=prop_log_limit)

def add_update_prop_time(_lock_time, _base_update_time, _prop_view_time, _total):
    lock_time.append(_lock_time)
    base_update_time.append(_base_update_time)
    prop_view_time.append(_prop_view_time)
    total_update_prop_time.append(_total)

def get_update_prop_time():
    if len(lock_time) <= 10:
        if len(total_read_prop_time) > 10: return -1, -1, -1, get_read_prop_time()
        return -1, -1, -1, -1
    return get_stable_average(lock_time, 2),\
           get_stable_average(base_update_time, 2),\
           get_stable_average(prop_view_time, 2),\
           get_stable_average(total_update_prop_time, 2)


# read_prop_time
total_read_prop_time = deque(maxlen=prop_log_limit)

def add_read_prop_time(prop_time):
    total_read_prop_time.append(prop_time)

def get_read_prop_time():
    if len(total_read_prop_time) <= 10:
        if len(lock_time) > 10: return get_update_prop_time()[3]
        return -1
    return get_stable_average(total_read_prop_time, 2)


# commit_prop_time
total_commit_prop_time = deque(maxlen=prop_log_limit)

def add_commit_prop_time(prop_time):
    total_commit_prop_time.append(prop_time)

def get_commit_prop_time():
    if len(total_commit_prop_time) == 0:
        return -1
    return get_stable_average(total_commit_prop_time, 2)



is_r_peer = {}
is_edge_r_peer = {}
r_direction = {}

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



leaf_distance = defaultdict(dict)           # leaf_distance[lineage][dir_peer_name] = leaf distance
update_req_num = defaultdict(int)           # update_req_num[lineage] = # update request        @ config.peer_name
read_req_num = defaultdict(int)             # read_req_num[lineage] = # read request            @ config.peer_name
fetch_req_num = defaultdict(int)            # fetch_req_num[lineage] = # fetch request          @ config.peer_name
fetch_num = defaultdict(int)                # fetch_num[lineage] = # fetch                      @ config.peer_name
r_around_peers = defaultdict(set)           # r_around_peers[lineage] = R-around peers          @ config.peer_name

def init_ec_setting(lineage):
    leaf_distance[lineage] = {}
    update_req_num[lineage] = 0
    read_req_num[lineage] = 0
    fetch_req_num[lineage] = 0
    fetch_num[lineage] = 0
    r_around_peers[lineage] = set()

def get_max_leaf_distance(lineage, target_peer):
    if not get_is_r_peer(lineage) or target_peer not in get_r_direction(lineage): return None
    update_prop_time = get_update_prop_time()[3]
    if update_prop_time == -1: return None
    max_leaf_distance = 0
    for dir_peer in get_r_direction(lineage):
        if dir_peer == target_peer: continue
        if lineage not in leaf_distance or dir_peer not in leaf_distance[lineage]: return None
        if not leaf_distance[lineage][dir_peer]: return None
        max_leaf_distance = max(max_leaf_distance, leaf_distance[lineage][dir_peer])
    return max_leaf_distance + update_prop_time

def get_radius(lineage):
    if not get_is_r_peer(lineage): return float("inf")
    if get_update_prop_time()[3] == -1: return float("inf")
    radius = 0
    for dir_peer in get_r_direction(lineage):
        if lineage not in leaf_distance or dir_peer not in leaf_distance[lineage]: return float("inf")
        if not leaf_distance[lineage][dir_peer]: return float("inf")
        radius = max(radius, leaf_distance[lineage][dir_peer])
    return radius



# CostReductionSimulator
class CostReductionSimulator:
    # heap function
    def heap_push(self, heap, value):
        heapq.heappush(heap, (-value[0], value[1], value[2], value[3]))
    def heap_top(self, heap):
        leaf_distance, dir_peer, leaf_peer, used = heap[0]
        return (-leaf_distance, dir_peer, leaf_peer, used)
    def heap_pop(self, heap):
        leaf_distance, dir_peer, leaf_peer, used = heapq.heappop(heap)
        return (-leaf_distance, dir_peer, leaf_peer, used)

    def dfs_from_center(self, current_peer_name, parent_peer_name, dir_peer_name, distance):
        current_peer = self.peers[current_peer_name]
        self.distance[current_peer_name] = distance   # distance
        if current_peer["is_leaf"]:
            self.dir_max_leaf_distance[dir_peer_name] = max(self.dir_max_leaf_distance[dir_peer_name], distance)   # dir_max_leaf_distance
            self.dir_leaf_peers[dir_peer_name].append(current_peer_name)   # dir_leaf_peers
        if current_peer["is_r_neighbor"]:
            self.dir_r_neighbor_peers[dir_peer_name].append(current_peer_name)   # dir_r_neighbor_peers
        self.dir_update_req_num[dir_peer_name] += current_peer["update_req_num"]   # dir_update_req_num

        for next_peer_name in self.edges[current_peer_name]:
            if next_peer_name == parent_peer_name: continue
            next_peer = self.peers[next_peer_name]
            if current_peer_name == self.center_peer_name:
                dir_peer_name = next_peer_name
            self.dfs_from_center(next_peer_name, current_peer_name, dir_peer_name, distance + next_peer["update_prop_time"])

    def init(self):
        center_peer_name = self.center_peer_name

        for peer_name in self.edges[center_peer_name]:
            if self.peers[peer_name]["is_r"]:
                self.dir_peers.append(peer_name)

        for peer_name in self.peers:
            peer = self.peers[peer_name]
            self.update_req_num_total += peer["update_req_num"]
            self.read_req_num[peer_name] = peer["read_req_num"]
            self.fetch_num[peer_name] = peer["fetch_num"]
            for r_around_peer_name in peer["r_around_peers"]:
                self.read_req_num[peer_name] += self.peers[r_around_peer_name]["read_req_num"]
                self.fetch_num[peer_name] += self.peers[r_around_peer_name]["fetch_num"]

        self.dfs_from_center(center_peer_name, center_peer_name, center_peer_name, 0)

    def __init__(self, peers, edges, center_peer_name):
        # self.lineage = lineage
        self.peers = peers
        self.edges = edges
        self.center_peer_name = center_peer_name

        self.dir_peers = []
        self.update_req_num_total = 0
        self.distance = {}   # distance[peer_name] = distance from center
        self.dir_max_leaf_distance = defaultdict(int)   # dir_max_leaf_distance[dir_peer_name] = max leaf distance
        self.dir_leaf_peers = defaultdict(list)
        self.dir_r_neighbor_peers = defaultdict(list)
        self.dir_update_req_num = defaultdict(int)
        self.read_req_num = defaultdict(int)   # read_req_num[r_neighbor_peer_name] = # read requests
        self.fetch_num = defaultdict(int)   # fetch_num[r_neighbor_peer_name] = # fetch

        self.init()


    def get_update_req_num(self, dir_peers):
        update_req_num = 0
        for dir_peer_name in dir_peers:
            update_req_num += self.dir_update_req_num[dir_peer_name]
        return update_req_num

    def get_max_leaf_distance(self, dir_peers):
        max_leaf_distance = 0
        for dir_peer_name in dir_peers:
            max_leaf_distance = max(max_leaf_distance, self.dir_max_leaf_distance[dir_peer_name])
        return max_leaf_distance

    def get_max_leaf_distance_from(self, target_dir_peer_name):
        max_leaf_distance = 0
        for dir_peer_name in self.dir_peers:
            if dir_peer_name == target_dir_peer_name: continue
            max_leaf_distance = max(max_leaf_distance, self.dir_max_leaf_distance[dir_peer_name])
        return max_leaf_distance

    def get_fetch_num(self, peer_name):
        peer = self.peers[peer_name]
        if not peer["is_leaf"]: return self.fetch_num[peer_name]
        update_req_num = self.update_req_num_total - peer["update_req_num"]
        local_read_req_num = peer["read_req_num"]
        local_update_req_num = peer["update_req_num"]
        N = update_req_num + local_update_req_num + self.read_req_num[peer_name]
        local_fetch_num = local_read_req_num * (update_req_num + 1) / N
        return local_fetch_num + self.fetch_num[peer_name]


    # get_target_profit_list
    def get_target_profit_list(self, target_dir_peers, initial_revenue):
        # create heap
        heap_for_target = []
        for dir_peer_name in self.dir_peers:
            if dir_peer_name in target_dir_peers: continue
            for leaf_peer_name in self.dir_leaf_peers[dir_peer_name]:
                value = (-self.distance[leaf_peer_name], dir_peer_name, leaf_peer_name, False)
                heap_for_target.append(value)
        heapq.heapify(heap_for_target)

        # contraction
        used_leaf_peers = []
        update_req_num = self.get_update_req_num(target_dir_peers)
        if heap_for_target:
            target_profit = [initial_revenue, self.heap_top(heap_for_target)[0], set(), set()]   # profit, max distance, contraction peers, expansion peers
        else:
            target_profit = [0, 0, set(), set()]
        while heap_for_target:
            leaf_distance, dir_peer_name, leaf_peer_name, used = self.heap_pop(heap_for_target)
            if used: break
            used_leaf_peers.append(leaf_peer_name)
            leaf_peer = self.peers[leaf_peer_name]
            self.heap_push(heap_for_target, (leaf_distance-leaf_peer["update_prop_time"], dir_peer_name, leaf_peer_name, True))

            next_leaf = self.heap_top(heap_for_target)
            revenue = update_req_num * (leaf_distance - next_leaf[0])
            expense = self.get_fetch_num(leaf_peer_name) * leaf_peer["read_prop_time"]
            profit = revenue - expense

            target_profit[0] += profit
            target_profit[1] = next_leaf[0]
            target_profit[2].add(leaf_peer_name)

        # create heap
        heap_for_target = []
        for dir_peer_name in set(self.dir_peers) | set([self.center_peer_name]):
            if dir_peer_name in target_dir_peers: continue
            # original
            for leaf_peer_name in self.dir_leaf_peers[dir_peer_name]:
                if leaf_peer_name in used_leaf_peers:
                    value = (self.distance[leaf_peer_name], dir_peer_name, leaf_peer_name, "original")
                    heap_for_target.append(value)
            # expanded
            for r_neighbor_peer_name in self.dir_r_neighbor_peers[dir_peer_name]:
                if r_neighbor_peer_name in used_leaf_peers: continue
                for r_around_peer_name in self.peers[r_neighbor_peer_name]["r_around_peers"]:
                    value = (self.distance[r_around_peer_name], dir_peer_name, r_around_peer_name, "expanded")
                    heap_for_target.append(value)
        heapq.heapify(heap_for_target)

        # expansion
        max_peer_distance = target_profit[1]
        target_profit_list = [copy.deepcopy(target_profit)]
        while heap_for_target:
            # if not heap_for_target: break
            new_distance, dir_peer_name, peer_name, state = heapq.heappop(heap_for_target)
            peer = self.peers[peer_name]
            if state == "original" and peer["is_r_neighbor"]:
                for r_around_peer_name in peer["r_around_peers"]:
                    info = (self.distance[r_around_peer_name], dir_peer_name, r_around_peer_name, "expanded")
                    heapq.heappush(heap_for_target, info)

            revenue = self.get_fetch_num(peer_name) * peer["read_prop_time"]
            expense = 0
            if max_peer_distance < new_distance:
                expense = update_req_num * (new_distance - max_peer_distance)
                max_peer_distance = new_distance
            profit = revenue - expense

            target_profit[0] += profit
            target_profit[1] = new_distance
            if state == "original":
                target_profit[2].remove(peer_name)
            else:
                target_profit[3].add(peer_name)
            target_profit_list.append(copy.deepcopy(target_profit))

        return target_profit_list


    # calculate_optimal_solution
    def calculate_optimal_solution(self, target_dir_peer_name):
        # target_profit_list
        target_dir_peers = set([target_dir_peer_name])
        initial_revenue = 0
        target_profit_list = self.get_target_profit_list(target_dir_peers, initial_revenue)

        # non_target_profit_list
        non_target_dir_peers = set(self.dir_peers) - set([target_dir_peer_name]) | set([self.center_peer_name])
        for dir_peer in non_target_dir_peers:
            diff_distance = self.get_max_leaf_distance_from(dir_peer) - self.dir_max_leaf_distance[target_dir_peer_name]
            initial_revenue += self.dir_update_req_num[dir_peer] * diff_distance
        non_target_profit_list = self.get_target_profit_list(non_target_dir_peers, initial_revenue)

        # max_overall_profit
        max_overall_profit = [0, set(), set()]
        max_target_profit = [-float("inf"), set(), set()]
        target_i = 0
        non_target_i = 0
        while True:
            target_info = target_profit_list[target_i]
            non_target_info = non_target_profit_list[non_target_i]
            if math.isclose(target_info[1], non_target_info[1]) or target_info[1] < non_target_info[1]:
                if max_target_profit[0] < target_info[0]:
                    max_target_profit = target_info
                overall_profit = max_target_profit[0] + non_target_info[0]
                overall_contracted_peers = max_target_profit[2] | non_target_info[2]
                overall_expanded_peers = max_target_profit[3] | non_target_info[3]
                if max_overall_profit[0] < overall_profit:
                    max_overall_profit = [overall_profit, overall_contracted_peers, overall_expanded_peers]
            if target_i < len(target_profit_list)-1 and \
               (math.isclose(target_profit_list[target_i+1][1], non_target_info[1]) or \
                             target_profit_list[target_i+1][1] < non_target_info[1]):
                target_i += 1
            else:
                if non_target_i == len(non_target_profit_list)-1: break
                non_target_i += 1

        # print(target_dir_peer_name)
        # print(target_profit_list)
        # print(non_target_profit_list)
        # print(max_overall_profit)

        # ec_info
        ec_info = defaultdict(list)
        for old_peer_name in max_overall_profit[1]:
            new_peer_name = self.peers[old_peer_name]["r_direction"][0]
            ec_info[old_peer_name].append(("contraction_old", new_peer_name))
            ec_info[new_peer_name].append(("contraction_new", old_peer_name))
        for new_peer_name in max_overall_profit[2]:
            old_peer_name = self.peers[new_peer_name]["r_direction"][0]
            ec_info[new_peer_name].append(("expansion_new", old_peer_name))
            ec_info[old_peer_name].append(("expansion_old", new_peer_name))
        solution = (max_overall_profit[0], ec_info)

        return solution


    # calculate_optimal_solution
    def calculate_optimal_solution_for_singleton(self):
        # create heap
        heap_for_target = []
        for r_around_peer_name in self.peers[self.center_peer_name]["r_around_peers"]:
            value = (self.distance[r_around_peer_name], self.center_peer_name, r_around_peer_name, "expanded")
            heap_for_target.append(value)
        heapq.heapify(heap_for_target)

        # expansion
        update_req_num = self.peers[self.center_peer_name]["update_req_num"]
        max_peer_distance = 0
        overall_profit = [0, set(), set()]
        max_overall_profit = [0, set(), set()]
        while True:
            if not heap_for_target: break
            new_distance, dir_peer_name, peer_name, state = heapq.heappop(heap_for_target)
            peer = self.peers[peer_name]

            revenue = self.read_req_num[peer_name] * peer["read_prop_time"]
            expense = update_req_num * (new_distance - max_peer_distance)
            max_peer_distance = new_distance
            profit = revenue - expense

            overall_profit[0] += profit
            overall_profit[2].add(peer_name)
            if max_overall_profit[0] < overall_profit[0]:
                max_overall_profit = overall_profit

        # ec_info
        ec_info = defaultdict(list)
        for new_peer_name in max_overall_profit[2]:
            old_peer_name = self.peers[new_peer_name]["r_direction"][0]
            ec_info[new_peer_name].append(("expansion_new", old_peer_name))
            ec_info[old_peer_name].append(("expansion_old", new_peer_name))

        return ec_info



# ec_test
def ec_test(peers, edges, center_peer_name):
    cost_reduction_simulator = CostReductionSimulator(peers, edges, center_peer_name)

    optimal_solution = [0, {}]
    for dir_peer_name in cost_reduction_simulator.dir_peers:
        solution = cost_reduction_simulator.calculate_optimal_solution(dir_peer_name)
        if optimal_solution[0] < solution[0]: optimal_solution = solution
    ec_info = optimal_solution[1]

    if not cost_reduction_simulator.dir_peers:
        ec_info = cost_reduction_simulator.calculate_optimal_solution_for_singleton()
    # print(f"center: {center_peer_name},   ec_info = {ec_info}")

    return ec_info




# r_direction
# is_r_peer
# is_edge_r_peer
def execute_ec(lineage, ec_info_list):
    for ec_info in ec_info_list:
        partner_peer_name = ec_info[1]
        if ec_info[0] == "expansion_old":
            r_direction[lineage].add(partner_peer_name)
            is_edge_r_peer[lineage] = (len(r_direction[lineage]) <= 1)

        elif ec_info[0] == "expansion_new":
            r_direction[lineage] = set([partner_peer_name])
            is_r_peer[lineage] = True
            is_edge_r_peer[lineage] = True

        elif ec_info[0] == "contraction_old":
            r_direction[lineage] = set([partner_peer_name])
            is_r_peer[lineage] = False
            is_edge_r_peer[lineage] = False

        elif ec_info[0] == "contraction_new":
            r_direction[lineage].remove(partner_peer_name)
            is_edge_r_peer[lineage] = (len(r_direction[lineage]) <= 1)

        else:
            raise Exception


def get_deletion_insertion_set(delta):
    deletion_set = set()
    insertion_set = set()
    for dt in delta:
        deletion_set |= set([deletion["lineage"] for deletion in delta[dt]["deletions"]])
        insertion_set |= set([insertion["lineage"] for insertion in delta[dt]["insertions"]])
    init_adr_setting_if_not(insertion_set)
    return deletion_set, insertion_set
