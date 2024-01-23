import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
import config
import measurement

class Unlock(data_pb2_grpc.UnlockServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)

        global_xid = params['xid']

        measurement.time_measurement.start_timer("lock_process", global_xid)
        if global_xid in config.tx_dict:
            tx = config.tx_dict[global_xid]
            tx.abort()
            del config.tx_dict[global_xid]
        measurement.time_measurement.stop_timer("lock_process", global_xid)

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))