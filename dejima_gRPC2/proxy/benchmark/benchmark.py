import json
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from benchmark.worker import Worker
from benchmark.management import BenchmarkManagement
from benchmark.tenv.procedures import tenv_tx

class Benchmark(data_pb2_grpc.BenchmarkServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        params = json.loads(req.json_str)
        bench_name = params["bench_name"]

        if bench_name == "tenv":
            res_dic = tenv_tx.execute(params)
            return data_pb2.Response(json_str=json.dumps(res_dic))

        worker = Worker()
        result = None
        params["benchmark_management"] = BenchmarkManagement(bench_name)
        result = worker.execute(params)

        if not result: print("result is None")
        res_dic = result
        return data_pb2.Response(json_str=json.dumps(res_dic))
