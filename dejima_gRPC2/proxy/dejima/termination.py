import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import dejimautils

class Termination(data_pb2_grpc.TerminationServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)

        if params['result'] == "commit":
            commit = True
        else:
            commit = False

        global_xid = params['xid']
        tx = config.tx_dict[global_xid]

        # termination 
        if commit:
            tx.commit()
            dejimautils.termination_request("commit", global_xid, params["method"]) 
        else:
            tx.abort()
            dejimautils.termination_request("abort", global_xid, params["method"]) 

        del config.tx_dict[global_xid]
        del config.prop_visited[global_xid]

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))