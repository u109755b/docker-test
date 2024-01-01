import json
import data_pb2
import data_pb2_grpc
from benchmark.ycsb.ycsb_load import YCSBLoad
from benchmark.tpcc.tpcc_load_local import TPCCLoadLocal
from benchmark.tpcc.tpcc_load_customer import TPCCLoadCustomer

class LoadData(data_pb2_grpc.LoadDataServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        params = json.loads(req.json_str)
        bench_name = params["bench_name"]

        result = None
        if bench_name == "tpcc":
            if params["data_name"] == "local":
                tpcc_load_local = TPCCLoadLocal()
                result = tpcc_load_local.load(params)
            if params["data_name"] == "customer":
                tpcc_load_customer = TPCCLoadCustomer()
                result = tpcc_load_customer.load(params)

        if bench_name == "ycsb":
            ycsb_load = YCSBLoad()
            result = ycsb_load.load(params)

        if not result: print("result is None")
        res_dic = {"result": result["result"]}
        return data_pb2.Response(json_str=json.dumps(res_dic))
