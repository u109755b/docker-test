import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import requester

class ECTest(data_pb2_grpc.ECTestServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)
        operation_type = params["operation_type"]
        lineage = params["lineage"]
        global_params = params['global_params']
        parent_peer = global_params["parent_peer"]

        requester.ec_test(operation_type, lineage, global_params)

        res_dic = {"result": "Ack"}
        if operation_type == "get_leaf_distance":
            # max_leaf_distance
            if adrutils.get_is_r_peer(lineage):
                max_leaf_distance = adrutils.get_max_leaf_distance(lineage, parent_peer)
                if max_leaf_distance: res_dic["max_leaf_distance"] = (config.peer_name, max_leaf_distance)
            # peers
            res_dic["peers"] = global_params["peers"]
            # edges
            res_dic["edges"] = global_params["edges"]
        if operation_type == "get_center_peer":
            # center_peer_info
            res_dic["center_peer_info"] = global_params["center_peer_info"]
        return data_pb2.Response(json_str=json.dumps(res_dic))
