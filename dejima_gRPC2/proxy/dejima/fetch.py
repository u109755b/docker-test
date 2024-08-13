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
        if global_xid not in config.tx_dict:
            tx = Tx(global_xid, params["start_time"])
        else:
            tx = config.tx_dict[global_xid]

        lineage_set = set(params["lineages"])
        lineage_set.discard("dummy")


        # at an adr peer
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        # if config.peer_name in config.adr_peers:
        is_r_peer = adrutils.get_is_r_peer(list(params["lineages"])[0])
        for lineage in params["lineages"]:
            if adrutils.get_is_r_peer(lineage) != is_r_peer:
                print(f"{os.path.basename(__file__)}: error lineage set")
                raise Exception
        if is_r_peer:
            expansion_lineages = adrutils.countup_request(lineage_set, "read", params["parent_peer"])
            adrutils.ec_execute({"lineages": expansion_lineages, "parent_peer": params["parent_peer"]}, "expansion", "old")
            if expansion_lineages:
                res_dic["expansion_data"] = {"peer": config.peer_name, "lineages": expansion_lineages}
            latest_data_dict = {}
            for dt in config.dt_list:
                if not lineage_set: break
                lineage_col_name, condition =  dejimautils.get_where_condition(dt, lineage_set)
                tx.cur.execute(f"SELECT * FROM {dt} WHERE {condition} FOR SHARE")
                latest_data = tx.cur.fetchall()
                latest_data_dict[dt] = latest_data
            res_dic["latest_data_dict"] = latest_data_dict
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))


        # at a non-adr peer
        # lock with lineages
        res_dic = {"result": "Nak"}
        res_dic["peer_name"] = config.peer_name
        try:
            dejimautils.lock_with_lineages(tx, params["lineages"], for_what="UPDATE")

        except errors.RecordsNotFound as e:
            print(f"{os.path.basename(__file__)}: global lock failed (Not Found)")
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # propagate latest data from other peers
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        result = requester.fetch_request(params["lineages"], params["xid"], params["start_time"], params["global_params"])
        if "latest_data_dict" not in params["global_params"]:
            return data_pb2.Response(json_str=json.dumps(res_dic))
        latest_data_dict = params["global_params"]["latest_data_dict"]

        local_xid = tx.get_local_xid()
        dejimautils.execute_fetch(local_xid, latest_data_dict, tx.cur.execute)

        # propagate to dejima table
        prop_dict = {}
        for dt in config.dt_list:
            delta = dejimautils.propagate_to_dt(dt, local_xid, tx.cur)
            if delta:
                prop_dict[dt] = delta
        res_dic["latest_data_dict"] = prop_dict

        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
