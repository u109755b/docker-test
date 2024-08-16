import json
import time
import os
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


class CheckLatest(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("check_latest")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)
        global_xid = params['xid']
        global_params = params["global_params"]


        # at a non-adr peer
        is_r_peers = adrutils.get_is_r_peers(params["lineages"])
        if not is_r_peers:
            result = requester.check_latest_request(params["lineages"], params["xid"], params["start_time"], global_params)
            res_dic = {"result": result}
            if result == "Ack":
                tx = Tx(global_xid, params["start_time"])
                tx.extend_childs(global_params["peer_names"])
                res_dic["fetch_lineages"] = global_params["fetch_lineages"]
                res_dic["peer_name"] = config.peer_name
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))


        # at an adr peer
        tx = Tx(global_xid, params["start_time"])
        adrutils.countup_request(params["lineages"], "read", global_params["parent_peer"])

        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_with_lineages(tx, params["lineages"], for_what="SHARE")

        except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            tx.abort()
            tx.close()
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # get timestamps and compare with requester ones
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        fetch_lineages = []
        expansion_lineages = []
        for lineage in params["lineages"]:
            requester_timestamp = global_params["timestamps"][lineage]
            latest_timestamp = dejimautils.get_timestamp(tx, lineage, to_isoformat=True)
            if requester_timestamp != latest_timestamp:
                fetch_lineages.append(lineage)
            else:
                expansion_lineages.append(lineage)

        # fetch_lineages
        res_dic["fetch_lineages"] = fetch_lineages
        # expansion
        expansion_lineages = adrutils.get_expansion_lineages(expansion_lineages, global_params["parent_peer"])
        adrutils.expansion_old(expansion_lineages, global_params["parent_peer"])
        if expansion_lineages:
            res_dic["expansion_data"] = {"peer": config.peer_name, "lineages": expansion_lineages}

        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
