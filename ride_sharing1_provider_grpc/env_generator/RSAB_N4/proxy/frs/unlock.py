import json
import config
import time
import data_pb2
import data_pb2_grpc

# class Unlock(object):
class Unlock(data_pb2_grpc.UnlockServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        # if req.content_length:
        #     body = req.bounded_stream.read()
        #     params = json.loads(body)
        params = json.loads(req.json_str)

        global_xid = params['xid']

        if global_xid in config.tx_dict:
            tx = config.tx_dict[global_xid]
            tx.abort()
            del config.tx_dict[global_xid]

        # resp.text = json.dumps({"result": "Ack"})
        # return
        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))