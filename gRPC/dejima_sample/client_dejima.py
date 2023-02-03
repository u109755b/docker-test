import pprint
import sys

# 「grpc」パッケージと、protocによって生成したパッケージをimportする
import grpc
import data_pb2
import data_pb2_grpc

import time
import json
import threading

peer_address = "localhost:1234"
# peer_address = "0.0.0.1:1234"

def lock_request():
    data = {
        "xid": "lock-xid",
        "lineages": ["lineage1", "lineage2"]
    }
    # req = data_pb2.LockRequest(xid="xid", lineages=["lineage1", "lineage2"])
    req = data_pb2.Request(json_str=json.dumps(data))
    service_stub = data_pb2_grpc.LockStub
    base_request(peer_address, service_stub, req)

def release_lock_request():
    data = {
        "xid": "unlock-xid"
    }
    # req = data_pb2.UnlockRequest(xid="xid")
    req = data_pb2.Request(json_str=json.dumps(data))
    service_stub = data_pb2_grpc.UnlockStub
    base_request(peer_address, service_stub, req)


def prop_request(method):
    data = {
        "xid": "prop-xid",
        "dejima_table": "d1_2",
        "delta": {"deletion": [{"a": 1}, {"b": 2}], "insertion": [{"c": 3}, {"d": 4}]},
        "parent_peer": "Peer1",
        "measure_time": False
    }
    req = data_pb2.Request(json_str=json.dumps(data))
    if method == "2pl":
        service_stub = data_pb2_grpc.TPLPropagationStub
    else:
        service_stub = data_pb2_grpc.FRSPropagationStub
    base_request(peer_address, service_stub, req)
    
def termination_request(method):
    data = {
        "xid": "termination-xid",
        "result": "commit"
    }
    req = data_pb2.Request(json_str=json.dumps(data))
    if method == "2pl":
        service_stub = data_pb2_grpc.TPLTerminationStub
    else:
        service_stub = data_pb2_grpc.FRSTerminationStub
    base_request(peer_address, service_stub, req)
    
    
def base_request(peer_address, service_stub, req):
    with grpc.insecure_channel(peer_address) as channel:
        stub = service_stub(channel)
        response = stub.on_post(req)
        params = json.loads(response.json_str)
    print(params)
        # print(response.result)
        # if str(response.json_str) == "":
        #     print("ok")
        # else:
        #     print(json.loads(response.json_str)["timestamps"])

def load_rsab():
    N = 5
    n = 10
    start_id = 1
    max_hop = 2
    data = {
        "start_id": start_id,
        "record_num": n,
        "step": N,
        "max_hop": max_hop
    }
    req = data_pb2.Request(json_str=json.dumps(data))
    # service_stub = data_pb2_grpc.RSABLoadStub
    # base_request(peer_address, service_stub, req)
    
    with grpc.insecure_channel(peer_address) as channel:
        stub = data_pb2_grpc.RSABLoadStub(channel)
        response = stub.on_get(req)
        params = json.loads(response.json_str)
        print(params)

def rsab():
    thread_list = []
    N = 5
    t = 10
    method = "2pl"
    threads = 1
    result_file = "result_file"
    data = {
        "bench_time": t,
        "method": method
    }
    req = data_pb2.Request(json_str=json.dumps(data))
    service_stub = data_pb2_grpc.RSABStub
    args = [peer_address, service_stub, req]
    # rsab_peer(peer_address, service_stub, req)
    for i in range(2):
        thread = threading.Thread(target=rsab_peer, args=args)
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
        
def rsab_peer(peer_address, service_stub, req):
    with grpc.insecure_channel(peer_address) as channel:
        stub = service_stub(channel)
        response = stub.on_get(req)
        params = json.loads(response.json_str)
        print(params)

if __name__ == '__main__':
    lock_request()
    release_lock_request()
    prop_request("2pl")
    prop_request("frs")
    termination_request("2pl")
    termination_request("frs")
    load_rsab()
    rsab()