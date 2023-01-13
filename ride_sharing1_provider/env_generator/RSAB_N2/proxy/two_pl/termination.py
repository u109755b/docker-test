import json
import dejimautils
import config
import time

class TPLTermination(object):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        if req.content_length:
            body = req.bounded_stream.read()
            params = json.loads(body)

        if params['result'] == "commit":
            commit = True
        else:
            commit = False

        global_xid = params['xid']
        tx = config.tx_dict[global_xid]

        # termination 
        if commit:
            tx.commit()
            dejimautils.termination_request("commit", global_xid, "2pl") 
        else:
            tx.abort()
            dejimautils.termination_request("abort", global_xid, "2pl") 

        del config.tx_dict[global_xid]

        msg = {"result": "Ack"}
        resp.text = json.dumps(msg)
        return