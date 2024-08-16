import json
import time
import os
from collections import deque
from opentelemetry import trace
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import errors
from dejima import dejimautils
from dejima import requester
from dejima.transaction import Tx

tracer = trace.get_tracer(__name__)


class Fetch(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("fetch")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)

        global_xid = params['xid']
        global_params = params["global_params"]
        tx = dejimautils.get_tx(global_xid, params["start_time"])


        # at an adr peer
        res_dic = {"result": "Ack"}

        is_r_peers = adrutils.get_is_r_peers(params["lineages"])
        if is_r_peers:
            # expansion test & expansion
            expansion_lineages = adrutils.get_expansion_lineages(params["lineages"], params["parent_peer"])
            adrutils.expansion_old(expansion_lineages, params["parent_peer"])
            if expansion_lineages:
                res_dic["expansion_data"] = {"peer": config.peer_name, "lineages": expansion_lineages}
            # get latest_data_dict
            latest_data_dict = {}
            for dt in config.dt_list:
                lineage_col_name, condition =  dejimautils.get_where_condition(dt, params["lineages"])
                tx.execute(f"SELECT * FROM {dt} WHERE {condition}")
                latest_data = tx.fetchall()
                latest_data_dict[dt] = latest_data
            res_dic["latest_data_dict"] = latest_data_dict
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))


        # at a non-adr peer
        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_with_lineages(tx, params["lineages"], for_what="UPDATE")

        except errors.RecordsNotFound as e:
            print(f"{os.path.basename(__file__)}: global lock failed (Not Found)")
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # propagate latest data from other peers
        result = requester.fetch_request(params["lineages"], params["xid"], params["start_time"], global_params)
        if result != "Ack":
            return data_pb2.Response(json_str=json.dumps(res_dic))

        local_xid = tx.get_local_xid()
        latest_data_dict = global_params["latest_data_dict"]
        dejimautils.execute_fetch(tx.execute, local_xid, latest_data_dict)


        # propagate to dejima table
        res_dic = {"result": "Ack"}
        prop_dict = {}
        for dt in config.dt_list:
            delta = dejimautils.propagate_to_dt(tx, dt, local_xid)
            if delta:
                prop_dict[dt] = delta
        res_dic["latest_data_dict"] = prop_dict

        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
