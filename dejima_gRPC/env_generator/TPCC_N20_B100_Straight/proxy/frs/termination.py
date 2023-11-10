import json
import dejimautils
import config
import time
import data_pb2
import data_pb2_grpc

# class FRSTermination(object):
class FRSTermination(data_pb2_grpc.FRSTerminationServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        # if req.content_length:
        #     body = req.bounded_stream.read()
        #     params = json.loads(body)
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
            dejimautils.termination_request("commit", global_xid, "frs") 
        else:
            tx.abort()
            dejimautils.termination_request("abort", global_xid, "frs") 

        del config.tx_dict[global_xid]

        # msg = {"result": "Ack"}
        # resp.text = json.dumps(msg)
        # return
        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))