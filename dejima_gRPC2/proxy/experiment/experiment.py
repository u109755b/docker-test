import threading
from grpcdata import data_pb2_grpc

from opentelemetry import trace
from opentelemetry.context import attach, detach, set_value

from experiment.exp_base import ExperimentBase

tracer = trace.get_tracer(__name__)


class Experiment(ExperimentBase):
    def __init__(self, bench_name):
        self.bench_name = bench_name

        self.peer_num = 3
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
                peer_name = f"Peer{i+1}"
                data = {
                    "about": parameter_name,
                    "parameter": parameter,
                }
                service_stub = data_pb2_grpc.ValChangeStub
                self.base_request(peer_name, data, service_stub, save_result=False, show_result=False)


    # load
    def base_load(self, peer_name, data, service_stub=None, save_result=False, show_result=True):
        if not service_stub:
            service_stub = data_pb2_grpc.LoadDataStub
        self.base_request(peer_name, data, service_stub, save_result=save_result, show_result=show_result)


    # execute
    def execute_benchmark(self, method):
        self.res_list = []
        data = {
            "bench_time": self.tx_t,
            "method": method,
        }
        service_stub = data_pb2_grpc.BenchmarkStub
        data["bench_name"] = self.bench_name

        with tracer.start_as_current_span("client_main") as span:
            ctx = set_value("current_span", span)
            thread_list = []
            print("bench {} {} {} {}".format(method, self.peer_num, self.threads, self.tx_t))
            for i in range(self.peer_num):
                for _ in range(self.threads):
                    peer_name = f"Peer{i+1}"
                    args = [peer_name, data, service_stub, ctx]
                    thread = threading.Thread(target=self.base_request, args=args)
                    thread_list.append(thread)

            for thread in thread_list:
                thread.start()
            for thread in thread_list:
                thread.join()

        self.integrate_result(self.res_list, self.peer_num, self.threads, show_result=True)
