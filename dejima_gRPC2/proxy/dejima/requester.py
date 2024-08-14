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
    params["peer_name"] = [None]
    params["latest_timestamps"] = []

    parent_peer = global_params.get("parent_peer")
    global_params["parent_peer"] = config.peer_name

    look_peers = [peer for lineage in lineages for peer in adrutils.get_r_direction(lineage)]

    for peer in look_peers:
        if peer == parent_peer: continue
        data = {
            "lineages": lineages,
            "xid": global_xid,
            "start_time": start_time,
            "global_params": global_params,
        }
        args = ([peer, data_pb2_grpc.CheckLatestStub, data, params])
        thread_list.append(threading.Thread(target=base_request, args=args))
    dejimautils.execute_threads(thread_list)

    global_params["peer_names"] = [peer for peer in params["peer_name"] if peer]
    latest_timestamps = {}
    latest_timestamps.update(*params["latest_timestamps"])
    global_params["latest_timestamps"] = latest_timestamps

    if all(params["results"]) and not latest_timestamps:
        print(f"latest_timestamps not found {params["results"]} {latest_timestamps} {config.peer_name} {look_peers} {len(thread_list)}")

    return "Ack" if all(params["results"]) else "Nak"


# fetch request
def fetch_request(lineages, global_xid, start_time, global_params={}):
    thread_list = []
    params = {"results": []}
    params["peer_name"] = [None]
    params["latest_data_dict"] = []
    params["expansion_data"] = []

    parent_peer = global_params.get("parent_peer")
    global_params["parent_peer"] = config.peer_name

    for peer in config.tx_dict[global_xid].child_peers:
        if peer == parent_peer: continue
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

    global_params["peer_names"] = [peer for peer in params["peer_name"] if peer]
    if params["latest_data_dict"]:
        global_params["latest_data_dict"] = params["latest_data_dict"][0]
    for expansion_data in params["expansion_data"]:
        adrutils.expansion_new(expansion_data["lineages"], expansion_data["peer"])

    return "Ack" if all(params["results"]) else "Nak"


# prop request
def prop_request(arg_dict, global_xid, start_time, method, global_params={}):
    thread_list = []
    params = {"results": []}
    params["peer_name"] = [None]
    params["contraction_data"] = []
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

    for contraction_data in params["contraction_data"]:
        adrutils.contraction_new(contraction_data["lineages"], contraction_data["peer"])

    global_params["peer_names"] = [peer for peer in params["peer_name"] if peer]
    if "max_hop" in global_params:
        if config.hop_mode: global_params["max_hop"] = max(params["max_hop"]) + 1
        else: global_params["max_hop"] = sum(params["max_hop"]) + 1
    if "timestamps" in global_params:
        global_params["timestamps"] = max(reversed(params["timestamps"]), key=len)

    return "Ack" if all(params["results"]) else "Nak"


# termination request
def termination_request(result, current_xid, method):
    thread_list = []
    params = {"results": []}

    for peer in config.tx_dict[current_xid].child_peers:
        data = {
            "xid": current_xid,
            "method": method,
            "result": result
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
            "peer_name", "max_hop",
            "latest_data_dict", "latest_timestamps",
            "expansion_data", "contraction_data"
        ]
        for append_name in append_list:
            if append_name in res_dic:
                params[append_name].append(res_dic[append_name])

    except Exception as e:
        print("base_request:", e)
        params["results"].append(False)
