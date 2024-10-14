import json
import time
import os
from collections import deque, defaultdict
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
        gp = global_params
        tx = dejimautils.get_tx(global_xid, params["start_time"])

        r_lineages = [lineage for lineage in params["lineages"] if adrutils.get_is_r_peer(lineage)]
        non_r_lineages = [lineage for lineage in params["lineages"] if not adrutils.get_is_r_peer(lineage)]

        latest_data_dict = defaultdict(dict)
        expansion_lineages = []
        res_dic = {"result": "Nak"}


        # at an adr peer
        if r_lineages:
            # expansion test & expansion
            expansion_lineages = adrutils.get_expansion_lineages(r_lineages, params["parent_peer"], gp["contraction_num"], gp["update_prop_time"], gp["read_prop_time"])
            adrutils.expansion_old(expansion_lineages, params["parent_peer"])

            # get latest_data_dict
            for dt in config.dt_list:
                lineage_col_name, condition =  dejimautils.get_where_condition(dt, r_lineages)
                tx.execute(f"SELECT * FROM {dt} WHERE {condition}")
                latest_data = tx.fetchall()
                latest_data_dict[dt] = {"update": latest_data}


        # at a non-adr peer
        if non_r_lineages:
            timestamp = []
            timestamp.append(time.perf_counter())   # 0

            # lock with lineages
            try:
                dejimautils.lock_with_lineages(tx, non_r_lineages, for_what="UPDATE")

            except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
                # print(f"{os.path.basename(__file__)}: global lock failed")
                return data_pb2.Response(json_str=json.dumps(res_dic))

            # propagate latest data from other peers
            timestamp.append(time.perf_counter())   # 1
            result = requester.fetch_request(non_r_lineages, params["xid"], params["start_time"], global_params)
            if result != "Ack":
                return data_pb2.Response(json_str=json.dumps(res_dic))

            # fetch to local
            timestamp.append(time.perf_counter())   # 2
            local_xid = tx.get_local_xid()
            ret_latest_data_dict = global_params["latest_data_dict"]
            dejimautils.execute_fetch(tx.execute, local_xid, ret_latest_data_dict)

            # propagate to dejima table
            for dt in config.dt_list:
                delta = dejimautils.propagate_to_dt(tx, dt, local_xid)
                if delta:
                    latest_data_dict[dt].update(delta)

            timestamp.append(time.perf_counter())   # 3
            adrutils.add_read_prop_time(timestamp[1]-timestamp[0] + timestamp[3]-timestamp[2])


        # return
        res_dic = {"result": "Ack"}
        res_dic["latest_data_dict"] = latest_data_dict
        if expansion_lineages:
            res_dic["expansion_data"] = {"peer": config.peer_name, "lineages": expansion_lineages}
        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))
