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
        parent_peer = global_params["parent_peer"]

        r_lineages = [lineage for lineage in params["lineages"] if adrutils.get_is_r_peer(lineage)]
        non_r_lineages = [lineage for lineage in params["lineages"] if not adrutils.get_is_r_peer(lineage)]

        all_peers = set([config.peer_name])
        fetch_lineages = []
        res_dic = {"result": "Nak"}


        # at an adr peer
        if r_lineages:
            tx = dejimautils.get_tx(global_xid, params["start_time"])

            # lock with lineages
            try:
                dejimautils.lock_with_lineages(tx, r_lineages, for_what="SHARE")

            except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
                # print(f"{os.path.basename(__file__)}: global lock failed")
                tx.abort()
                tx.close()
                return data_pb2.Response(json_str=json.dumps(res_dic))

            # get timestamps and compare with requester ones
            for lineage in r_lineages:
                requester_timestamp = global_params["timestamps"][lineage]
                latest_timestamp = dejimautils.get_timestamp(tx, lineage, to_isoformat=True)
                if requester_timestamp != latest_timestamp:
                    fetch_lineages.append(lineage)

            for lineage in r_lineages:
                adrutils.r_around_peers[lineage].add(parent_peer)


        # at a non-adr peer
        if non_r_lineages:
            result = requester.check_latest_request(non_r_lineages, params["xid"], params["start_time"], global_params)
            if result != "Ack":
                return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))

            tx = dejimautils.get_tx(global_xid, params["start_time"])
            tx.extend_childs(global_params["peer_names"], global_params["prop_num"])
            all_peers |= global_params["all_peers"]
            fetch_lineages += global_params["fetch_lineages"]


        # return
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name
        res_dic["all_peers"] = all_peers
        res_dic["fetch_lineages"] = fetch_lineages
        res_dic["r_lineages"] = r_lineages
        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))
