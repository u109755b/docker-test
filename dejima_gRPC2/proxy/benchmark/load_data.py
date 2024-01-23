import json
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from benchmark.tpcc import loader as tpcc_loader
from benchmark.ycsb import loader as ycsb_loader

class LoadData(data_pb2_grpc.LoadDataServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        params = json.loads(req.json_str)
        bench_name = params["bench_name"]

        result = None
        if bench_name == "tpcc":
            result = tpcc_loader.load(params)

        if bench_name == "ycsb":
            result = ycsb_loader.load(params)

        if not result: print("result is None")
        res_dic = {"result": result["result"]}
        return data_pb2.Response(json_str=json.dumps(res_dic))
