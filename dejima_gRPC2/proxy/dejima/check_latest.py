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
                res_dic["latest_timestamps"] = global_params["latest_timestamps"]
                res_dic["peer_name"] = config.peer_name
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))


        # at an adr peer
        tx = Tx(global_xid, params["start_time"])

        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_with_lineages(tx, params["lineages"], for_what="SHARE")

        except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            tx.abort()
            tx.close()
            return data_pb2.Response(json_str=json.dumps(res_dic))


        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        latest_timestamps = {}
        for lineage in params["lineages"]:
            latest_timestamp = dejimautils.get_timestamp(tx, lineage, to_isoformat=True)
            latest_timestamps[lineage] = latest_timestamp

        if not latest_timestamps:
            print("latest_timestamps is empty")
        res_dic["latest_timestamps"] = latest_timestamps
        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
