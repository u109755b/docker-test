import time
import json
import threading
from collections import deque
from collections import defaultdict
import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import dejimautils


# lock request
def lock_request(lineages, global_xid, start_time):
    thread_list = []
    params = {"results": []}

    for peer in config.target_peers:
        data = {
            "lineages": lineages,
            "xid": global_xid,
            "start_time": start_time,
            "parent_peer": config.peer_name,
        }
        args = ([peer, data_pb2_grpc.LockStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    return "Ack" if all(params["results"]) else "Nak"


# release lock request
def release_lock_request(global_xid):
    thread_list = []
    params = {"results": []}

    for peer in config.target_peers:
        data = {
            "xid": global_xid
        }
        args = ([peer, data_pb2_grpc.UnlockStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    return "Ack" if all(params["results"]) else "Nak"


# check latest request
def check_latest_request(lineages, global_xid, start_time, global_params={}):
    thread_list = []
    params = {"results": []}
    params["peer_name"] = []
    params["all_peers"] = []
    params["fetch_lineages"] = []
    params["r_lineages"] = []

    parent_peer = global_params.get("parent_peer")
    global_params["parent_peer"] = config.peer_name

    look_peers = [peer for lineage in lineages for peer in adrutils.get_r_direction(lineage)]

    for peer in set(look_peers):
        if peer == parent_peer: continue
        global_params["update_prop_time"] = adrutils.get_update_prop_time()[3]
        global_params["read_prop_time"] = adrutils.get_read_prop_time()
        data = {
            "lineages": lineages,
            "xid": global_xid,
            "start_time": start_time,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.CheckLatestStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    global_params["peer_names"] = params["peer_name"]
    global_params["all_peers"] = set().union(*params["all_peers"])
    global_params["fetch_lineages"] = list(set().union(*params["fetch_lineages"]))
    for r_lineages in params["r_lineages"]:
        for lineage in r_lineages:
            adrutils.read_req_num[lineage] += 1

    return "Ack" if all(params["results"]) else "Nak"


# fetch request
def fetch_request(lineages, global_xid, start_time, global_params={}):
    thread_list = []
    params = {"results": []}
    params["latest_data_dict"] = []
    params["expansion_data"] = []

    parent_peer = global_params.get("parent_peer")
    global_params["parent_peer"] = config.peer_name

    for peer in config.tx_dict[global_xid].child_peers[global_params["prop_num"]]:
        if peer == parent_peer: continue
        global_params["update_prop_time"] = adrutils.get_update_prop_time()[3]
        global_params["read_prop_time"] = adrutils.get_read_prop_time()
        data = {
            "lineages": lineages,
            "xid": global_xid,
            "start_time": start_time,
            "parent_peer": config.peer_name,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.FetchStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    if all(params["results"]):
        global_params["latest_data_dict"] = defaultdict(lambda: defaultdict(list))
        for latest_data_dict in params["latest_data_dict"]:
            for dt, delta in latest_data_dict.items():
                for key in delta:
                    if key == "view": global_params["latest_data_dict"][dt][key] = delta[key]
                    else: global_params["latest_data_dict"][dt][key] += delta[key]

    return "Ack" if all(params["results"]) else "Nak"


# expansion and contraction test
# 1st call: calculate leaf distance
# 2nd call: calculate the center of the R tree
# 3rd call: expand and contract
def ec_test(operation_type, lineage, global_params={}):
    thread_list = []
    params = {"results": []}

    params["max_leaf_distance"] = []
    params["peers"] = []
    params["edges"] = []
    params["center_peer_info"] = []

    parent_peer = global_params.get("parent_peer", config.peer_name)
    global_params["parent_peer"] = config.peer_name
    if "max_leaf_distance" in global_params:
        adrutils.leaf_distance[lineage][parent_peer] = global_params["max_leaf_distance"]

    dir_r_peers = set(adrutils.get_r_direction(lineage))   # to R peers
    dir_r_around_peers = set(adrutils.r_around_peers[lineage]) - set([config.peer_name])   # to R-around peers
    for peer in dir_r_peers | dir_r_around_peers:
        if peer == parent_peer: continue
        if operation_type == "get_center_peer":
            max_leaf_distance = adrutils.get_max_leaf_distance(lineage, peer)
            if max_leaf_distance: global_params["max_leaf_distance"] = max_leaf_distance
        data = {
            "operation_type": operation_type,
            "lineage": lineage,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.ECTestStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    if operation_type == "get_leaf_distance":
        # max_leaf_distance
        for dir_peer_name, max_leaf_distance in params["max_leaf_distance"]:
            adrutils.leaf_distance[lineage][dir_peer_name] = max_leaf_distance
        # peers
        global_params["peers"] = {}
        for peers_dict in params["peers"]:
            global_params["peers"].update(peers_dict)
        if adrutils.get_is_r_peer(lineage) or adrutils.read_req_num[lineage]:
            global_params["peers"][config.peer_name] = {
                "is_r": adrutils.get_is_r_peer(lineage),
                "is_leaf": adrutils.get_is_edge_r_peer(lineage),
                "is_r_neighbor": len(dir_r_around_peers) != 0,
                "is_r_around": not adrutils.get_is_r_peer(lineage) and adrutils.read_req_num[lineage] != 0,
                "r_direction": list(adrutils.get_r_direction(lineage)),
                "r_around_peers": list(dir_r_around_peers),
                "update_prop_time": adrutils.get_update_prop_time()[3],
                "read_prop_time": adrutils.get_read_prop_time(),
                "update_req_num": adrutils.update_req_num[lineage],
                "read_req_num": adrutils.read_req_num[lineage],
                "fetch_num": adrutils.fetch_num[lineage],
            }
        # edges
        global_params["edges"] = defaultdict(list)
        for edges_dict in params["edges"]:
            global_params["edges"].update(edges_dict)
        if adrutils.get_is_r_peer(lineage) or adrutils.read_req_num[lineage]:
            for peer in dir_r_peers | dir_r_around_peers:
                if peer == parent_peer: continue
                global_params["edges"][config.peer_name].append(peer)
                global_params["edges"][peer].append(config.peer_name)
    if operation_type == "get_center_peer":
        # center_peer_info
        center_peer_info = (config.peer_name, adrutils.get_radius(lineage))
        for peer_name, radius in params["center_peer_info"]:
            if center_peer_info[1] > radius:
                center_peer_info = (peer_name, radius)
        global_params["center_peer_info"] = center_peer_info
    # if "ec_info" in global_params:
    if operation_type == "expand_contract":
        if config.peer_name in global_params["ec_info"]:
            adrutils.execute_ec(lineage, global_params["ec_info"][config.peer_name])
        adrutils.init_ec_setting(lineage)

    return "Ack" if all(params["results"]) else "Nak"


# prop request
def prop_request(arg_dict, global_xid, start_time, method, global_params={}):
    thread_list = []
    params = {"results": []}
    params["peer_name"] = []
    params["all_peers"] = []
    params["update_req_num_total"] = []
    params["first_r_peer"] = []
    if "max_hop" in global_params: params["max_hop"] = [0]
    if "timestamps" in global_params: params["timestamps"] = [[]]

    peers = set()
    dts_delta = defaultdict(dict)
    for dt in arg_dict.keys():
        for peer in arg_dict[dt]["peers"]:
            delta = arg_dict[dt]["delta"]
            if config.adr_mode and not global_params.get("is_load", False):
                delta = {
                    "view": arg_dict[dt]["delta"]["view"],
                    "insertions": [insertion for insertion in arg_dict[dt]["delta"]["insertions"]
                                   if peer in adrutils.get_r_direction(insertion["lineage"])],
                    "deletions": [deletion for deletion in arg_dict[dt]["delta"]["deletions"]
                                  if peer in adrutils.get_r_direction(deletion["lineage"])]
                }
            if not delta["insertions"] and not delta["deletions"]: continue
            peers.add(peer)
            dts_delta[peer][dt] = delta

    if config.adr_mode and not global_params.get("is_load", False):
        ret_first_r_peer = {}
        for lineage in global_params["update_lineages"]:
            if adrutils.get_is_r_peer(lineage) and lineage not in global_params["first_r_peer"]:
                global_params["first_r_peer"][lineage] = config.peer_name
                ret_first_r_peer[lineage] = config.peer_name

    global_params["parent_peer"] = config.peer_name
    for peer in peers:
        data = {
            "xid": global_xid,
            "start_time": start_time,
            "method": method,
            "delta": dts_delta[peer],
            "parent_peer": config.peer_name,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.PropagationStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    global_params["peer_names"] = params["peer_name"]
    global_params["all_peers"] = set().union(*params["all_peers"])

    if config.adr_mode and not global_params.get("is_load", False):
        global_params["update_req_num_total"] = {}
        for lineage in global_params["update_lineages"]:
            global_params["update_req_num_total"][lineage] = adrutils.update_req_num[lineage]
        for update_req_num_total_dict in params["update_req_num_total"]:
            for lineage, update_req_num_total in update_req_num_total_dict.items():
                global_params["update_req_num_total"][lineage] += update_req_num_total

        for first_r_peer in params["first_r_peer"]:
            ret_first_r_peer.update(first_r_peer)
        global_params["first_r_peer"] = ret_first_r_peer

    if "max_hop" in global_params:
        if config.hop_mode: global_params["max_hop"] = max(params["max_hop"]) + 1
        else: global_params["max_hop"] = sum(params["max_hop"]) + 1
    if "timestamps" in global_params:
        global_params["timestamps"] = max(reversed(params["timestamps"]), key=len)

    return "Ack" if all(params["results"]) else "Nak"


# termination request
def termination_request(result, current_xid, global_params={}):
    thread_list = []
    params = {"results": []}

    if "first_r_peer" in global_params:
        for lineage, first_r_peer in global_params["first_r_peer"].items():
            if first_r_peer != config.peer_name: continue
            adrutils.update_req_num[lineage] += 1

    tx = config.tx_dict[current_xid]
    if config.termination_method == "all": peers = tx.child_peers_all
    else: peers = set().union(*tx.child_peers.values())

    for peer in peers:
        data = {
            "result": result,
            "xid": current_xid,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.TerminationStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    return "Ack" if all(params["results"]) else "Nak"


# base request
def base_request(peer, service_stub, data, params={}):
    try:
        peer_address = config.dejima_config_dict['peer_address'][peer]
        if peer_address not in config.channels:
            config.channels[peer_address] = grpc.insecure_channel(peer_address)
        stub = service_stub(config.channels[peer_address])
        req = data_pb2.Request(json_str=json.dumps(data))
        res = stub.on_post(req)
        res_dic = json.loads(res.json_str)
    
        if res_dic['result'] == "Ack":
            params["results"].append(True)
        else:
            params["results"].append(False)

        if "timestamps" in res_dic:
            res_dic["timestamps"][-1].append(time.perf_counter())   # 5
            params["timestamps"].append(res_dic["timestamps"])

        append_list = [
            "peer_name", "all_peers", "max_hop", "fetch_lineages",
            "latest_data_dict", "expansion_data", "contraction_data",
            "max_leaf_distance", "peers", "edges", "center_peer_info",
            "r_lineages", "update_req_num_total", "first_r_peer",
        ]
        for append_name in append_list:
            if append_name in res_dic:
                params[append_name].append(res_dic[append_name])

    except Exception as e:
        print("base_request:", e)
        params["results"].append(False)
