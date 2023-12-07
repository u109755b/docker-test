# 「grpc」パッケージと、protocによって生成したパッケージをimportする
import grpc
import data_pb2
import data_pb2_grpc
import utils

import time
import json
import threading
import sys
import re
import numpy as np

class Experiment():
    def __init__(self):
        self.peer_num=2
        self.threads=1   # num of threads for each peer
        self.record_num=100
        self.tx_t=10
        self.test_time=600
        self.tpcc_record_num=10

        self.default_zipf=0.99     # zipf
        self.prelock_invalid=False
        self.plock_mode=True
        self.hop_mode=False

        self.res_list = []
    
    
    def show_parameter(self):
        # print('peer_num: {}'.format(self.peer_num))
        # print('threads: {}'.format(self.threads))
        print('tpcc_record_num: {}'.format(self.tpcc_record_num))


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
                "record_num": self.tpcc_record_num,
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)


    def set_prelock_invalid(self):
        print("set_prelock_invalid {}".format(self.prelock_invalid))
        for i in range(self.peer_num):
            data = {
                "about": "prelock_invalid",
                "prelock_invalid": self.prelock_invalid,
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)


    def set_plock_mode(self):
        print("set_plock_mode {}".format(self.plock_mode))
        for i in range(self.peer_num):
            data = {
                "about": "plock_mode",
                "plock_mode": self.plock_mode,
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)


    def set_hop_mode(self):
        print("set_hop_mode {}".format(self.hop_mode))
        for i in range(self.peer_num):
            data = {
                "about": "hop_mode",
                "hop_mode": self.hop_mode,
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)


    def initialize(self):
        print("initialize")
        for i in range(self.peer_num):
            data = {
                "about": "initialize",
            }
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(i, data, service_stub, show_result=False)


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
        print("bench {} {} {} {}".format(method, self.peer_num, self.threads, self.tx_t))
        for i in range(self.peer_num):
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

        # 結果の統合
        process_time_keys = ['lock', 'base_update', 'prop_view_0', 'view_update', 'prop_view_k', 'communication', 'commit']
        thread_num = self.peer_num * self.threads

        all_data = {
            "basic_res": {
                "commit": [0, 0, 0],
                "abort": [0, 0, 0],
                "commit_time": [0, 0, 0],
                "abort_time": [0, 0, 0],
                "custom_commit": [0, 0, 0],
                "custom_abort": [0, 0, 0],
                "global_lock": [0],
            },
            "process_time": {k: 0 for k in process_time_keys},
            "lock_process": [0],
        }

        divider_data = {
            "basic_res": {
                "commit": [1, 1, 1],
                "abort": [1, 1, 1],
                "commit_time": [thread_num, thread_num, thread_num],
                "abort_time": [thread_num, thread_num, thread_num],
                "custom_commit": [1, 1, 1],
                "custom_abort": [1, 1, 1],
                "global_lock": [thread_num],
            },
            "process_time": {k: thread_num for k in process_time_keys},
            "lock_process": [thread_num],
        }

        basic_res = all_data["basic_res"]
        process_time = all_data["process_time"]
        global_lock = all_data["basic_res"]["global_lock"]
        lock_process = all_data["lock_process"]

        # 結果の合計
        for res in self.res_list:
            res = json.loads(res)
            plus = lambda x, y: x + y
            utils.general_2obj_func(all_data, res, plus, save=True)

        # 結果の割り算
        utils.general_2obj_func(all_data, divider_data, utils.divide, save=True)

        # 全ピアにおける平均伝搬範囲を求める
        basic_res["custom_commit"][2] = utils.divide(basic_res["custom_commit"][0], basic_res["custom_commit"][1])
        basic_res["custom_abort"][2] = utils.divide(basic_res["custom_abort"][0], basic_res["custom_abort"][1])

        # 小数第2位に丸める
        utils.general_1obj_func(all_data, utils.round2, save=True)

        # その他の計算
        tx_time = basic_res["commit_time"][0] + basic_res["abort_time"][0]
        throughput = basic_res["commit"][0] / tx_time
        custom_throughput = basic_res["custom_commit"][0] / tx_time

        commit_time = basic_res["commit_time"][0]

        commit_per_peer = basic_res["commit"][0] / self.peer_num
        commit_time_per_commit = utils.divide(commit_time, commit_per_peer) * 1000
        global_lock_time_per_commit = utils.divide(global_lock[0], commit_per_peer) * 1000

        overall_result = [throughput, custom_throughput, commit_time, global_lock[0], commit_time_per_commit, global_lock_time_per_commit]
        utils.general_1obj_func(overall_result, utils.round2, save=True)

        # 結果表示
        print("throughput: {} {},  ({} {})[s],  ({} {})[ms]".format(*overall_result))
        print("commit:  {} ({} {})  {} ({} {})[s],   {} = {} * {}".format(*basic_res["commit"], *basic_res["commit_time"], *basic_res["custom_commit"]))
        print("abort:  {} ({} {})  {} ({} {})[s],   {} = {} * {}".format(*basic_res["abort"], *basic_res["abort_time"], *basic_res["custom_abort"]))
        print("{}, {}[ms]".format(process_time, utils.round2(lock_process[0])))



args = sys.argv
bench_type=args[1]
command_name=int(args[2])

experiment = Experiment()
if command_name == 0:
    experiment.load_tpcc()

if command_name == 1:
    experiment.set_zipf()
    experiment.set_prelock_invalid()
    experiment.set_plock_mode()
    experiment.set_hop_mode()
    experiment.show_parameter()

    print("")
    experiment.initialize()
    experiment.tpcc("2pl")

    print("")
    experiment.initialize()
    experiment.tpcc("frs")
