import threading
import json
from grpcdata import data_pb2_grpc

from opentelemetry import trace
from opentelemetry.context import attach, detach, set_value

from experiment.exp_base import ExperimentBase

tracer = trace.get_tracer(__name__)
from experiment.experiment import Experiment

class ExperimentTENV(Experiment):
    # show parameters
    def show_parameter(self):
        pass


    # load data
    def load_data(self):
        pass


    # execute
    def execute_benchmark(self):
        self.res_list = []
        data = {}
        service_stub = data_pb2_grpc.BenchmarkStub
        data["bench_name"] = self.bench_name
        self.peer_num = 1
        self.threads = 1




        while True:
            stmt = input("SQL input statement: ")
            if stmt == "exit": break

            data["stmt"] = stmt




            with tracer.start_as_current_span("client_main") as span:
                ctx = set_value("current_span", span)
                thread_list = []
                # print("bench {}".format(stmt))
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

            latest_result = json.loads(self.res_list[-1])["result"]
            print(f"result: {latest_result}")
        # self.integrate_result(self.res_list, self.peer_num, self.threads, show_result=True)