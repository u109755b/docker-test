import os
import json
import time
from collections import deque
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import errors
from dejima import dejimautils
from dejima import requester
from dejima.transaction import Tx

class Propagation(data_pb2_grpc.PropagationServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        timestamp = []
        timestamp.append(time.perf_counter())   # 0

        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)


        global_xid = params['xid']

        if global_xid not in config.tx_dict:
            tx = Tx(global_xid, params["start_time"])
        else:
            tx = config.tx_dict[global_xid]

        if global_xid not in config.prop_visited:
            is_first_time = True
            config.prop_visited[global_xid] = True
        else:
            is_first_time = False

        res_dic = {"result": "Nak", "peer_name": config.peer_name}
        if not is_first_time:
            res_dic["peer_name"] = None


        # count up update request
        if config.adr_mode:
            deletion_set = set()
            insertion_set = set()
            for dt in params["delta"]:
                deletion_set |= set([deletion["lineage"] for deletion in params["delta"][dt]["deletions"]])
                insertion_set |= set([insertion["lineage"] for insertion in params["delta"][dt]["insertions"]])
            for lineage in insertion_set:
                if lineage not in adrutils.is_r_peer:
                    adrutils.init_adr_setting(lineage)
            contraction_lineages = adrutils.countup_request(deletion_set & insertion_set, "update", params["parent_peer"])
            adrutils.ec_execute(contraction_lineages, "contraction", "old")
            if contraction_lineages:
                params["delta"] = []
                res_dic["contraction_data"] = {"peer": config.peer_name, "lineages": contraction_lineages}

        # update base tables according to updates to dt
        local_xid = tx.get_local_xid()
        try:
            # additional lock for peers out of lock scope
            lock_stmts = []
            for dt in params["delta"]:
                lock_stmts += dejimautils.get_lock_stmts(params['delta'][dt])
            if params["method"] == "2pl":
                dejimautils.lock_records(tx, lock_stmts, max_retry_cnt=3, min_miss_cnt=1, wait_die=True)
            else:
                dejimautils.lock_records(tx, lock_stmts, max_retry_cnt=3, min_miss_cnt=1)
        except errors.RecordsNotFound as e:
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))
        timestamp.append(time.perf_counter())   # 1

        try:
            # execute stmt
            for dt in params["delta"]:
                stmt = dejimautils.get_execute_stmt(params['delta'][dt], local_xid)
                tx.cur.execute(stmt)
        except Exception as e:
            if "stmt" in locals():
                print(stmt)
            errors.out_err(e, "dejima table update error", out_trace=True)
            return data_pb2.Response(json_str=json.dumps(res_dic))
        timestamp.append(time.perf_counter())   # 2


        # propagate to dejima table
        try: 
            prop_dict = {}
            for dt in config.dt_list:
                target_peers = [peer for peer in config.dejima_config_dict["dejima_table"][dt] 
                                if peer != config.peer_name and peer != params["parent_peer"]]
                if not target_peers: continue

                delta = dejimautils.propagate_to_dt(dt, local_xid, tx.cur)

                if delta:
                    prop_dict[dt] = {"peers": target_peers, "delta": delta}

        except Exception as e:
            if str(e).startswith("the JSON object must be str, bytes or bytearray"):
                print("delta:", delta)
            errors.out_err(e, "BIRDS execution error", out_trace=True)
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # propagate to other peers
        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = requester.prop_request(prop_dict, global_xid, params["start_time"], params["method"], params['global_params'])
            tx.extend_childs(params["global_params"]["peer_names"])
        else:
            result = "Ack"
        timestamp.append(time.perf_counter())   # 4


        if result != "Ack":
            res_dic = {"result": "Nak"}
        else:
            res_dic = {"result": "Ack"}

        # peer_name
        res_dic["peer_name"] = config.peer_name
        if not is_first_time:
            res_dic["peer_name"] = None
        # max_hop
        if "max_hop" in params["global_params"]:
            res_dic["max_hop"] = params["global_params"]["max_hop"]
        # timestamp
        if "timestamps" in params["global_params"] and result == "Ack":
            res_dic["timestamps"] = params["global_params"]["timestamps"]
            res_dic["timestamps"].append(timestamp)
        # contraction_data
        if contraction_lineages:
            res_dic["contraction_data"] = {"peer": config.peer_name, "lineages": contraction_lineages}
        return data_pb2.Response(json_str=json.dumps(res_dic))
