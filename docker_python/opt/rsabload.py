import grpc
import data_pb2
import data_pb2_grpc
import json
import sys

# 引数をチェックする
if (len(sys.argv) < 4):
    print("4 argument required")
    print("usage: {} <N> <n> <start_id> <max_hop>".format(sys.argv[0]))
    exit()

N = sys.argv[1]     # num of peers
n = sys.argv[2]     # num of records for each peer's insert
start_id = sys.argv[3]      # start id
max_hop = sys.argv[4]       # max hop

if (not N.isdigit()) or (not n.isdigit()):
    print("Invalid argument.")
    exit()
if (not start_id.isdigit()) or (not max_hop.isdigit()):
    print("Invalid argument.")
    exit()
N = int(N)
t = int(n)
start_id = int(start_id)
max_hop = int(max_hop)

for i in range(N):
    data = {
        "start_id": start_id+i,
        "record_num": n,
        "step": N,
        "max_hop": max_hop
    }
    req = data_pb2.Request(json_str=json.dumps(data))
    # with grpc.insecure_channel("localhost:{}".format(8001+i)) as channel:
    peer_address = "Peer{}-proxy:8000".format(i+1)
    with grpc.insecure_channel(peer_address) as channel:
        stub = data_pb2_grpc.RSABLoadStub(channel)
        response = stub.on_get(req)
        params = json.loads(response.json_str)
        print("Peer{}: {}".format(i+1, params["result"]))