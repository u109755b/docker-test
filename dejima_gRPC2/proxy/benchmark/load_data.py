import json
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from benchmark.management import BenchmarkManagement

# return {"result": str}
class LoadData(data_pb2_grpc.LoadDataServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        params = json.loads(req.json_str)
        bench_name = params["bench_name"]

        if not "data_name" in params:
            params["data_name"] = bench_name

        benchmark_management = BenchmarkManagement(bench_name)
        loader = benchmark_management.get_loader(params)
        result = loader.load(params)

        if not result: print("result is None")
        res_dic = {"result": result["result"]}
        return data_pb2.Response(json_str=json.dumps(res_dic))
