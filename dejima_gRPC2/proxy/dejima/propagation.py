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
        global_params = params['global_params']
        tx = dejimautils.get_tx(global_xid, params["start_time"])

        if global_xid not in config.prop_visited:
            is_first_time = True
            config.prop_visited[global_xid] = True
        else:
            is_first_time = False

        res_dic = {"result": "Nak"}
        if is_first_time:
            res_dic["peer_name"] = config.peer_name
        res_dic["all_peers"] = set([config.peer_name])
        if "max_hop" in global_params:
            res_dic["max_hop"] = global_params["max_hop"]


        # count up update request
        if config.adr_mode:
            deletion_set = set()
            insertion_set = set()
            for dt in params["delta"]:
                deletion_set |= set([deletion["lineage"] for deletion in params["delta"][dt]["deletions"]])
                insertion_set |= set([insertion["lineage"] for insertion in params["delta"][dt]["insertions"]])
            adrutils.init_adr_setting_if_not(insertion_set)
            adrutils.countup_request(deletion_set & insertion_set, "update", params["parent_peer"])

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
        except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))
        timestamp.append(time.perf_counter())   # 1

        # contraction test
        if config.adr_mode:
            contraction_lineages = adrutils.get_contraction_lineages(deletion_set & insertion_set, params["parent_peer"], global_params["expansion_num"])
            adrutils.contraction_old(contraction_lineages, params["parent_peer"])
            if contraction_lineages:
                res_dic["contraction_data"] = {"peer": config.peer_name, "lineages": contraction_lineages}

        try:
            # execute stmt
            for dt in params["delta"]:
                stmt = dejimautils.get_execute_stmt(params['delta'][dt], local_xid)
                tx.execute(stmt)
        except Exception as e:
            errors.out_err(e, "dejima table update error", out_trace=True)
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))
        timestamp.append(time.perf_counter())   # 2


        # propagate to dejima table
        try: 
            prop_dict = {}
            for dt in config.dt_list:
                target_peers = [peer for peer in config.dejima_config_dict["dejima_table"][dt] 
                                if peer != config.peer_name and peer != params["parent_peer"]]
                if not target_peers: continue

                delta = dejimautils.propagate_to_dt(tx, dt, local_xid)

                if delta:
                    prop_dict[dt] = {"peers": target_peers, "delta": delta}

        except Exception as e:
            errors.out_err(e, "BIRDS execution error", out_trace=True)
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))


        # propagate to other peers
        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = requester.prop_request(prop_dict, global_xid, params["start_time"], params["method"], global_params)
            tx.extend_childs(global_params["peer_names"], global_params["prop_num"])
            res_dic["all_peers"] |= global_params["all_peers"]
        else:
            result = "Ack"
        timestamp.append(time.perf_counter())   # 4
        adrutils.add_update_prop_time(timestamp[1]-timestamp[0], timestamp[2]-timestamp[1], timestamp[3]-timestamp[2], timestamp[3]-timestamp[0])


        # return
        res_dic["result"] = result
        if "timestamps" in global_params and result == "Ack":
            res_dic["timestamps"] = global_params["timestamps"]
            res_dic["timestamps"].append(timestamp)
        if "max_hop" in global_params:
            res_dic["max_hop"] = global_params["max_hop"]
        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.json_converter))
