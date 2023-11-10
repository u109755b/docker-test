# 「grpc」パッケージと、protocによって生成したパッケージをimportする
import grpc
import data_pb2
import data_pb2_grpc

import time
import json
import threading
import sys
import re

class Experiment():
    def __init__(self):
        self.threads=1   # num of threads for each peer
        self.peer_num=2
        self.record_num=100
        self.tx_t=100
        self.test_time=600
        self.default_zipf=0.99     # zipf
        
        self.res_list = []
    
    
    def base_request(self, i, data, service_stub, show_result=True):
        req = data_pb2.Request(json_str=json.dumps(data))
        peer_address = "Peer{}-proxy:8000".format(i+1)
        with grpc.insecure_channel(peer_address) as channel:
            stub = service_stub(channel)
            response = stub.on_get(req)
            params = json.loads(response.json_str)
            if show_result:
                print("Peer{}: {}".format(i+1, params["result"]))
    

    def load_tpcc(self):    
        print("load_tpcc {}".format(self.peer_num))
        
        print("local load")
        for i in range(self.peer_num):
            data = {
                "peer_num": self.peer_num,
            }
            service_stub = data_pb2_grpc.TPCCLoadLocalStub
            self.base_request(i, data, service_stub)
        
        print("customer load")
        for i in range(self.peer_num):
            data = {
                "peer_num": self.peer_num,
            }
            service_stub = data_pb2_grpc.TPCCLoadCustomerStub
            self.base_request(i, data, service_stub)


    def set_zipf(self):
        skew=self.default_zipf
        print("set_zipf {}".format(skew))
        for i in range(self.peer_num):
            data = {
                "about": "zipf",
                "theta": skew,
                # "record_num": self.record_num*self.peer_num,
                "record_num": 10,
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)
        print("finished")


    def tpcc_peer(self, peer_address, service_stub, req):
        self.res_list = []
        with grpc.insecure_channel(peer_address) as channel:
            stub = service_stub(channel)
            response = stub.on_get(req)
            self.res_list.append(response.json_str)

    def tpcc(self, method):
        thread_list = []
        data = {
            "bench_time": self.tx_t,
            "method": method,
        }
        print("bench {} {}".format(method, self.tx_t))
        for i in range(self.peer_num):
            if i == 1:
                i = 19
            for _ in range(self.threads):
                # peer_address = "localhost:{}".format(8001+i)
                peer_address = "Peer{}-proxy:8000".format(i+1)
                service_stub = data_pb2_grpc.TPCCStub
                req = data_pb2.Request(json_str=json.dumps(data))
                args = [peer_address, service_stub, req]
                thread = threading.Thread(target=self.tpcc_peer, args=args)
                thread_list.append(thread)
            
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        
        # 結果の計算
        commit_result_list = []
        abort_result_list = []
        for res in self.res_list:
            pattern = r'([\d.]+) \(([\d.]+) ([\d.]+)\)  ([\d.]+) \(([\d.]+) ([\d.]+)\)'
            matches = re.findall(pattern, res)
            commit_result_list.append(matches[0])
            abort_result_list.append(matches[1])
        commit_result = [sum(map(float, x)) for x in zip(*commit_result_list)]
        abort_result = [sum(map(float, x)) for x in zip(*abort_result_list)]
        for i in range(3, 6):
            commit_result[i] /= self.peer_num * self.threads
            abort_result[i] /= self.peer_num * self.threads
        commit_result = [int(item) if item.is_integer() else round(item, 2) for item in commit_result]
        abort_result = [int(item) if item.is_integer() else round(item, 2) for item in abort_result]
        print("throughput: {:.2f}".format(commit_result[0] / (commit_result[3]+abort_result[3])))
        print("commit:  {} ({} {})  {} ({} {})[s]".format(*commit_result))
        print("abort:  {} ({} {})  {} ({} {})[s]".format(*abort_result))



args = sys.argv
bench_type=args[1]
command_name=int(args[2])

experiment = Experiment()
if command_name == 0:
    experiment.load_tpcc()
if command_name == 1:
    experiment.set_zipf()
    print("")
    experiment.tpcc("2pl")
    print("")
    experiment.tpcc("frs")
