import json
import threading
import sys

import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.context import attach, detach, set_value

import config
import utils

if config.trace_enabled:
    resource = Resource(attributes={"service.name": "dejima_client"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(endpoint="http://{}:4317".format(config.host_name), insecure=True)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )
    GrpcInstrumentorClient().instrument()

tracer = trace.get_tracer(__name__)


class Experiment():
    def __init__(self, bench_name):
        self.bench_name = bench_name

        self.peer_num = 2
        self.threads = 1   # num of threads for each peer
        self.tx_t = 10
        self.test_time = 600

        self.default_zipf=0.99     # zipf

        self.tpcc_record_num = 10   # per peer
        self.yscb_start_id = 1
        self.ycsb_record_num = 100   # per peer

        self.prelock_request_invalid = False
        self.prelock_invalid = False
        self.hop_mode = False
        self.include_getting_tx_time = True
        self.getting_tx = True

        self.res_list = []


    def show_parameter(self):
        if self.bench_name == "tpcc":
            print("tpcc_record_num: {}".format(self.tpcc_record_num))
        if self.bench_name == "ycsb":
            print("ycsb_record_num: {}".format(self.ycsb_record_num))


    def base_request(self, i, data, service_stub, show_result=True):
        req = data_pb2.Request(json_str=json.dumps(data))
        peer_address = "Peer{}-proxy:8000".format(i+1)
        with grpc.insecure_channel(peer_address) as channel:
            stub = service_stub(channel)
            response = stub.on_get(req)
            params = json.loads(response.json_str)
            if show_result:
                print("Peer{}: {}".format(i+1, params["result"]))


    def load_tpcc(self, data, service_stub):
        print("local load")
        for i in range(self.peer_num):
            data["data_name"] = "local"
            self.base_request(i, data, service_stub)
        print("customer load")
        for i in range(self.peer_num):
            data["data_name"] = "customer"
            self.base_request(i, data, service_stub)

    def load_ycsb(self, data, service_stub):
        for i in range(self.peer_num):
            self.base_request(i, data, service_stub)
            data["start_id"] += 1


    def load_data(self):
        service_stub = data_pb2_grpc.LoadDataStub
        if self.bench_name == "tpcc":
            print("load_tpcc {}".format(self.peer_num))
            data = {
                "bench_name": self.bench_name,
                "peer_num": self.peer_num,
            }
            self.load_tpcc(data, service_stub)

        if self.bench_name == "ycsb":
            print("load_ycsb {} {} {}".format(self.yscb_start_id, self.ycsb_record_num, self.peer_num))
            data = {
                "bench_name": self.bench_name,
                "start_id": self.yscb_start_id,
                "record_num": self.ycsb_record_num,
                "step": self.peer_num,
            }
            self.load_ycsb(data, service_stub)


    def set_parameters(self):
        parameters = {
            "zipf": {"theta": self.default_zipf},
            "prelock_request_invalid": self.prelock_request_invalid,
            "prelock_invalid": self.prelock_invalid,
            "hop_mode": self.hop_mode,
            "include_getting_tx_time": self.include_getting_tx_time,
            "getting_tx": self.getting_tx,
        }
        if self.bench_name == "tpcc":
            parameters["zipf"]["record_num"] = self.tpcc_record_num   # ToDo: * self.peer_num
        if self.bench_name == "ycsb":
            parameters["zipf"]["record_num"] = self.ycsb_record_num * self.peer_num

        for parameter_name, parameter in parameters.items():
            print("set_{} {}".format(parameter_name, parameter))
            for i in range(self.peer_num):
                data = {
                    "about": parameter_name,
                    "parameter": parameter,
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


    def benchmark_per_peer(self, peer_address, service_stub, req, ctx):
        token = attach(ctx)
        self.res_list = []
        with grpc.insecure_channel(peer_address) as channel:
            stub = service_stub(channel)
            response = stub.on_get(req)
            self.res_list.append(response.json_str)
        detach(token)

    def execute_benchmark(self, method):
        data = {
            "bench_time": self.tx_t,
            "method": method,
        }
        service_stub = data_pb2_grpc.BenchmarkStub
        data["bench_name"] = self.bench_name

        with tracer.start_as_current_span("tpcc_client_main") as span:
            ctx = set_value("current_span", span)
            thread_list = []
            print("bench {} {} {} {}".format(method, self.peer_num, self.threads, self.tx_t))
            for i in range(self.peer_num):
                for _ in range(self.threads):
                    peer_address = "Peer{}-proxy:8000".format(i+1)
                    req = data_pb2.Request(json_str=json.dumps(data))
                    args = [peer_address, service_stub, req, ctx]
                    thread = threading.Thread(target=self.benchmark_per_peer, args=args)
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
bench_name=args[1]
command_name=int(args[2])

experiment = Experiment(bench_name)
if command_name == 0:
    experiment.load_data()

if command_name == 1:
    experiment.set_parameters()
    experiment.show_parameter()

    print("")
    experiment.initialize()
    experiment.execute_benchmark("2pl")

    print("")
    experiment.initialize()
    experiment.execute_benchmark("frs")
