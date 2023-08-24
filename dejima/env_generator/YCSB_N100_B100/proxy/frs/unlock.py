import json
import config
import time

class Unlock(object):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        if req.content_length:
            body = req.bounded_stream.read()
            params = json.loads(body)

        global_xid = params['xid']

        if global_xid in config.tx_dict:
            tx = config.tx_dict[global_xid]
            tx.abort()
            del config.tx_dict[global_xid]

        resp.text = json.dumps({"result": "Ack"})
        return