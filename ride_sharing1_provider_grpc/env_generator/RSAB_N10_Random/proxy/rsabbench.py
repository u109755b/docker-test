import grpc
import data_pb2
import data_pb2_grpc
import json
import threading
import sys

thread_list = []
lock = threading.Lock()
result = {"commit_num": 0, "abort_num": 0, "miss_num": 0}

# 引数をチェックする
if (len(sys.argv) < 6):
    print("5 argument required")
    print("usage: {} <N> <t> <method> <threads> <result_file>".format(sys.argv[0]))
    exit()

N = sys.argv[1]     # num of peers
t = sys.argv[2]     # time (s)
method = sys.argv[3]    # method
threads = sys.argv[4]   # # of threads for each peer
result_file = sys.argv[5]   # result file name

if (not N.isdigit()) or (not t.isdigit()) or (not threads.isdigit()):
    print("Invalid argument.")
    exit()
if method != "2pl" and method != "frs" and method != "hybrid":
    print("Invalid argument.")
    exit()
N = int(N)
t = int(t)
threads = int(threads)

data = {
    "bench_time": t,
    "method": method
}

def rsab_peer(peer_address, service_stub, req):
    with grpc.insecure_channel(peer_address) as channel:
        stub = service_stub(channel)
        response = stub.on_get(req)
        params = json.loads(response.json_str)
        print(params)
    if params["result"] != "Ack":
        return
    with lock:
        result["commit_num"] += params["commit_num"]
        result["abort_num"] += params["abort_num"]
        result["miss_num"] += params["miss_num"]
    result["throughput"] = result["commit_num"] / t

for i in range(N):
    for j in range(threads):
        peer_address = "localhost:{}".format(8001+i)
        service_stub = data_pb2_grpc.RSABStub
        req = data_pb2.Request(json_str=json.dumps(data))
        args = [peer_address, service_stub, req]
        thread = threading.Thread(target=rsab_peer, args=args)
        thread_list.append(thread)
    
for thread in thread_list:
    thread.start()
for thread in thread_list:
    thread.join()
print(result)
