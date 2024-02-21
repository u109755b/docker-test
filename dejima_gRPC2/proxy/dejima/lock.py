import json
import time
from opentelemetry import trace
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import errors
from dejima import measurement
from dejima import dejimautils
from dejima.transaction import Tx

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
            measurement.time_measurement.start_timer("lock_process", global_xid)
        if config.getting_tx:
            tx = Tx(global_xid, params["start_time"])
        if config.include_getting_tx_time == False:
            measurement.time_measurement.start_timer("lock_process", global_xid)


        # create lock statements
        bt_list = config.dejima_config_dict['base_table'][config.peer_name]
        bt_list = sum(bt_list.values(), [])
        lineage_set = set(params["lineages"])
        lineage_set.discard("dummy")
        lock_stmts = []

        for bt in bt_list:
            if bt == "customer":
                lineage_col_name = "c_lineage"   # hardcode (lineage name)
            else:
                lineage_col_name = "lineage"
            if not lineage_set: break
            conditions = " OR ".join([f"{lineage_col_name} = '{lineage}'" for lineage in lineage_set])
            lock_stmt = f"SELECT {lineage_col_name} FROM {bt} WHERE {conditions} FOR UPDATE"
            lock_stmts.append(lock_stmt)


        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_records(tx, lock_stmts, max_retry_cnt=0, min_miss_cnt=-1, wait_die=True)

        except errors.RecordsNotFound as e:
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))


        measurement.time_measurement.stop_timer("lock_process", global_xid)

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
