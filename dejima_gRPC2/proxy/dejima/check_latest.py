import json
import time
import os
from opentelemetry import trace
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import errors
from dejima import dejimautils
from dejima import requester
from dejima.transaction import Tx

tracer = trace.get_tracer(__name__)


class CheckLatest(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("check_latest")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)
        global_xid = params['xid']

        # at a non-adr peer
        # if config.peer_name not in config.adr_peers:
        is_r_peer = config.get_is_r_peer(list(params["lineages"])[0])
        for lineage in params["lineages"]:
            if config.get_is_r_peer(lineage) != is_r_peer:
                print(f"{os.path.basename(__file__)}: error lineage set")
                raise Exception
        if not is_r_peer:
            result = requester.check_latest_request(params["lineages"], params["xid"], params["start_time"], params["global_params"])
            res_dic = {"result": result}
            if result == "Ack" and params["global_params"]["peer_names"]:
                tx = Tx(global_xid, params["start_time"])
                tx.extend_childs(params["global_params"]["peer_names"])
                res_dic["latest_timestamps"] = params["global_params"]["latest_timestamps"]
                res_dic["peer_name"] = config.peer_name
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))

        if config.getting_tx:
            tx = Tx(global_xid, params["start_time"])

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
            lock_stmt = f"SELECT {lineage_col_name} FROM {bt} WHERE {conditions} FOR SHARE"
            lock_stmts.append(lock_stmt)


        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_records(tx, lock_stmts, max_retry_cnt=0, min_miss_cnt=-1, wait_die=True)

        except errors.RecordsNotFound as e:
            print(f"{os.path.basename(__file__)}: global lock failed (Not Found)")
            tx.abort()
            tx.close()
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            tx.abort()
            tx.close()
            return data_pb2.Response(json_str=json.dumps(res_dic))


        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        latest_timestamps = {}
        for dt in config.dt_list:
            if dt == "d_customer":
                lineage_col_name = "c_lineage"   # hardcode (lineage name)
            else:
                lineage_col_name = "lineage"
            for lineage in lineage_set:
                tx.cur.execute(f"SELECT updated_at FROM {dt} WHERE {lineage_col_name} = '{lineage}'")
                latest_timestamp, *_ = tx.cur.fetchone()
                latest_timestamps[lineage] = latest_timestamp

        if not latest_timestamps:
            print("latest_timestamps is empty")
        res_dic["latest_timestamps"] = latest_timestamps
        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
