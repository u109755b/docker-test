import json
import config
import time
from transaction import Tx
import data_pb2
import data_pb2_grpc

# class Lock(object):
class Lock(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)
        if config.prelock_valid:
            res_dic = {"result": "Ack"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        # if req.content_length:
        #     body = req.bounded_stream.read()
        #     params = json.loads(body)
        params = json.loads(req.json_str)

        global_xid = params['xid']
        tx = Tx(global_xid)
        config.tx_dict[global_xid] = tx

        # lock with lineages
        config.time_measurement.start_timer("lock_process", global_xid)
        bt_list = config.dejima_config_dict['base_table'][config.peer_name]
        # hardcode (lineage name)
        for bt in bt_list:
            if bt == "customer":
                lineage_col_name = "c_lineage"
            else:
                lineage_col_name = "lineage"
            stmt = "SELECT {} FROM {} WHERE ".format(lineage_col_name, bt) + " OR ".join(["{} = '{}'".format(lineage_col_name, lineage) for lineage in params['lineages']]) + " FOR UPDATE NOWAIT"

        try:
            if config.plock_mode:
                for lineage in params['lineages']:
                    config.lock_management.lock(global_xid, lineage)
            else:
                tx.cur.execute(stmt)
                result = tx.cur.fetchone()
                if result == None:
                    tx.abort()
                    del config.tx_dict[global_xid]
        except Exception as e:
            # # print("DB ERROR: ", e)
            # resp.text = json.dumps({"result": "Nak"})
            # return
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))
        config.time_measurement.stop_timer("lock_process", global_xid)
        
        # resp.text = json.dumps({"result": "Ack"})
        # return
        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
