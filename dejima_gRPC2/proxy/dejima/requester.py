import time
import json
import threading
from collections import deque
from collections import defaultdict
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.context import attach, detach, set_value
import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import dejimautils

if config.trace_enabled:
    GrpcInstrumentorClient().instrument()
tracer = trace.get_tracer(__name__)


def lock_request(lineages, global_xid, start_time):
    with tracer.start_as_current_span("lock_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        lock = threading.Lock()
        for peer in config.target_peers:
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.LockStub
            data = {
                "lineages": lineages,
                "xid": global_xid,
                "start_time": start_time,
                "parent_peer": config.peer_name,
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)

        dejimautils.execute_threads(thread_list)

        if all(results):
            return "Ack"
        else:
            return "Nak"

@tracer.start_as_current_span("release_request")
def release_lock_request(global_xid):
    thread_list = []
    results = []
    lock = threading.Lock()
    for peer in config.target_peers:
        peer_address = config.dejima_config_dict['peer_address'][peer]
        service_stub = data_pb2_grpc.UnlockStub
        data = {
            "xid": global_xid
        }
        req = data_pb2.Request(json_str=json.dumps(data))
        args = ([peer_address, service_stub, req, results, lock])
        thread = threading.Thread(target=base_request, args=args)
        thread_list.append(thread)

    dejimautils.execute_threads(thread_list)

    if all(results):
        return "Ack"
    else:
        return "Nak"

def check_latest_request(lineages, global_xid, start_time, global_params={}):
    with tracer.start_as_current_span("fetch_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        params = {}
        params["peer_name"] = [None]
        params["latest_timestamps"] = []
        lock = threading.Lock()

        parent_peer = None
        if "parent_peer" in global_params:
            parent_peer = global_params["parent_peer"]
        global_params["parent_peer"] = config.peer_name

        for peer in config.neighbor_peers:
            if peer == parent_peer: continue
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.CheckLatestStub
            data = {
                "lineages": lineages,
                "xid": global_xid,
                "start_time": start_time,
                "global_params": global_params,
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx, params])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)

        dejimautils.execute_threads(thread_list)

        peer_names = set(params["peer_name"])
        peer_names.remove(None)
        global_params["peer_names"] = list(peer_names)
        if params["latest_timestamps"]:
            global_params["latest_timestamps"] = params["latest_timestamps"][0]

        if all(results):
            return "Ack"
        else:
            return "Nak"

def fetch_request(lineages, global_xid, start_time, global_params={}):
    with tracer.start_as_current_span("fetch_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        params = {}
        params["peer_name"] = [None]
        params["latest_data_dict"] = []
        params["expansion_data"] = []
        lock = threading.Lock()

        parent_peer = None
        if "parent_peer" in global_params:
            parent_peer = global_params["parent_peer"]
        global_params["parent_peer"] = config.peer_name

        for peer in config.tx_dict[global_xid].child_peers:
            if peer == parent_peer: continue
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.FetchStub
            data = {
                "lineages": lineages,
                "xid": global_xid,
                "start_time": start_time,
                "parent_peer": config.peer_name,
                "global_params": global_params,
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx, params])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)

        dejimautils.execute_threads(thread_list)

        peer_names = set(params["peer_name"])
        peer_names.remove(None)
        global_params["peer_names"] = list(peer_names)
        if params["latest_data_dict"]:
            global_params["latest_data_dict"] = params["latest_data_dict"][0]
        if params["expansion_data"]:
            for expansion_data in params["expansion_data"]:
                for lineage in expansion_data["lineages"]:
                    config.is_r_peer[lineage] = True
                    config.is_edge_r_peer[lineage] = True
                    config.r_direction[lineage] = set([expansion_data["peer"]])
                    config.request_count[lineage] = deque()
                    print(f"expansion {lineage}: {expansion_data["peer"]} -> {config.peer_name}")

        if all(results):
            return "Ack"
        else:
            return "Nak"

def prop_request(arg_dict, global_xid, start_time, method, global_params={}):
    with tracer.start_as_current_span("prop_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        params = {}
        params["peer_name"] = [None]
        params["contraction_data"] = []
        if "max_hop" in global_params: params["max_hop"] = [0]
        if "timestamps" in global_params: params["timestamps"] = [[]]
        lock = threading.Lock()

        peers = set()
        dts_delta = defaultdict(dict)
        for dt in arg_dict.keys():
            for peer in arg_dict[dt]["peers"]:
                delta = arg_dict[dt]["delta"]
                if config.adr_mode:
                    if "is_load" not in global_params or global_params["is_load"] == False:
                        if config.peer_name in config.adr_peers and peer not in config.adr_peers:
                            continue
                        delta = {"view": arg_dict[dt]["delta"]["view"], "insertions": [], "deletions": []}
                        for insertion in arg_dict[dt]["delta"]["insertions"]:
                            lineage = insertion["lineage"]
                            if peer not in config.get_r_direction(lineage): continue
                            delta["insertions"].append(insertion)
                        for deletion in arg_dict[dt]["delta"]["deletions"]:
                            lineage = deletion["lineage"]
                            if peer not in config.get_r_direction(lineage): continue
                            delta["deletions"].append(deletion)
                if not delta["insertions"] and not delta["deletions"]: continue
                peers.add(peer)
                dts_delta[peer][dt] = delta

        for peer in peers:
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.PropagationStub
            data = {
                "xid": global_xid,
                "start_time": start_time,
                "method": method,
                "delta": dts_delta[peer],
                "parent_peer": config.peer_name,
                "global_params": global_params,
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx, params])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)

        dejimautils.execute_threads(thread_list)

        if params["contraction_data"]:
            for contraction_data in params["contraction_data"]:
                for lineage in contraction_data["lineages"]:
                    config.r_direction[lineage].remove(contraction_data["peer"])
                    if len(config.r_direction[lineage]) <= 1:
                        config.is_edge_r_peer[lineage] = True
                    config.request_count[lineage] = deque()
                    print(f"contraction {lineage}: {contraction_data["peer"]} -> {config.peer_name}")

        peer_names = set(params["peer_name"])
        peer_names.remove(None)
        global_params["peer_names"] = list(peer_names)
        if "max_hop" in global_params:
            if config.hop_mode: global_params["max_hop"] = max(params["max_hop"]) + 1
            else: global_params["max_hop"] = sum(params["max_hop"]) + 1
        if "timestamps" in global_params:
            global_params["timestamps"] = max(reversed(params["timestamps"]), key=len)

        if all(results):
            return "Ack"
        else:
            return "Nak"

def termination_request(result, current_xid, method):
    with tracer.start_as_current_span("termination_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        lock = threading.Lock()
        peers = config.tx_dict[current_xid].child_peers
        for peer in peers:
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.TerminationStub
            data = {
                "xid": current_xid,
                "method": method,
                "result": result
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)

        dejimautils.execute_threads(thread_list)

        if all(results):
            return "Ack"
        else:
            return "Nak"

def base_request(peer_address, service_stub, req, results, lock, ctx=None, params={}):
    try:
        if ctx: token = attach(ctx)
        
        # with tracer.start_as_current_span("base_request") as span:
        if peer_address not in config.channels:
            config.channels[peer_address] = grpc.insecure_channel(peer_address)
        stub = service_stub(config.channels[peer_address])
        res = stub.on_post(req)
        res_dic = json.loads(res.json_str)
        # with lock:
        if res_dic['result'] == "Ack":
            results.append(True)
        else:
            results.append(False)
        if "peer_name" in res_dic:
            params["peer_name"].append(res_dic["peer_name"])
        if "max_hop" in res_dic:
            params["max_hop"].append(res_dic["max_hop"])
        if "latest_data_dict" in res_dic:
            params["latest_data_dict"].append(res_dic["latest_data_dict"])
        if "latest_timestamps" in res_dic:
            params["latest_timestamps"].append(res_dic["latest_timestamps"])
        if "expansion_data" in res_dic:
            params["expansion_data"].append(res_dic["expansion_data"])
        if "contraction_data" in res_dic:
            params["contraction_data"].append(res_dic["contraction_data"])
        if "timestamps" in res_dic:
            res_dic["timestamps"][-1].append(time.perf_counter())   # 5
            params["timestamps"].append(res_dic["timestamps"])

        if ctx: detach(token)
    except Exception as e:
        print("base_request:", e)
        results.append(False)
        if ctx: detach(token)
