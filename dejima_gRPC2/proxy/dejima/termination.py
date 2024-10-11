import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import requester

class Termination(data_pb2_grpc.TerminationServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        timestamp = []
        timestamp.append(time.perf_counter())   # 0

        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)
        result = params["result"]
        global_xid = params['xid']
        tx = config.tx_dict[global_xid]


        if result == "commit": tx.commit()
        else: tx.abort()
        if config.termination_method == "neighbor":
            requester.termination_request(result, global_xid)
        tx.close()


        timestamp.append(time.perf_counter())   # 1
        adrutils.add_commit_prop_time(timestamp[1]-timestamp[0])

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
