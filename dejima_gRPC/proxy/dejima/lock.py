import json
import config
import time
from transaction import Tx
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class Lock(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("pre_lock")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)
        if config.prelock_invalid == True:
            res_dic = {"result": "Ack"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        params = json.loads(req.json_str)

        global_xid = params['xid']
        if config.include_getting_tx_time == True:
            config.time_measurement.start_timer("lock_process", global_xid)
        if config.getting_tx:
            tx = Tx(global_xid)
            config.tx_dict[global_xid] = tx
        if config.include_getting_tx_time == False:
            config.time_measurement.start_timer("lock_process", global_xid)

        # lock with lineages
        bt_list = config.dejima_config_dict['base_table'][config.peer_name]
        # hardcode (lineage name)
        for bt in bt_list:
            if bt == "customer":
                lineage_col_name = "c_lineage"
            else:
                lineage_col_name = "lineage"
            stmt = "SELECT {} FROM {} WHERE ".format(lineage_col_name, bt) + " OR ".join(["{} = '{}'".format(lineage_col_name, lineage) for lineage in params['lineages']]) + " FOR UPDATE NOWAIT"

        try:
            tx.cur.execute(stmt)
            result = tx.cur.fetchone()
            if result == None:
                tx.abort()
                del config.tx_dict[global_xid]
        except Exception as e:
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))
        config.time_measurement.stop_timer("lock_process", global_xid)

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
