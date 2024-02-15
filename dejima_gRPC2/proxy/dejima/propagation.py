import os
import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import errors
from dejima import dejimautils
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
        if global_xid in config.tx_dict:
            is_first_time = False
            tx = config.tx_dict[global_xid]
            locked_flag = True
        else:
            is_first_time = True
            tx = Tx(global_xid)
            config.tx_dict[global_xid] = tx
            locked_flag = False

        tx.propagation_cnt += 1
        if 1 < tx.propagation_cnt:
            pass
            # print(f"{global_xid}: A propagation was called {tx.propagation_cnt} times, from {params['parent_peer']}")
            # res_dic = {"result": "Nak"}
            # return data_pb2.Response(json_str=json.dumps(res_dic))

        # update dejima table and propagate to base tables
        local_xid = tx.get_local_xid()
        try:
            # additional lock for peers out of lock scope
            # if not locked_flag:
            lock_stmts = dejimautils.get_lock_stmts(params['delta'])
            for lock_stmt in lock_stmts:
                tx.cur.execute(lock_stmt)
            timestamp.append(time.perf_counter())   # 1

            # execute stmt
            stmt = dejimautils.get_execute_stmt(params['delta'], local_xid)
            tx.cur.execute(stmt)
            timestamp.append(time.perf_counter())   # 2

        except errors.LockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: global lock failed")
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except Exception as e:
            if "stmt" in locals():
                print(stmt)
            errors.out_err(e, "dejima table update error", out_trace=True)
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        try: 
            # propagation
            prop_dict = {}
            for dt in config.dt_list:
                # if dt == updated_dt: continue
                target_peers = list(config.dejima_config_dict['dejima_table'][dt])
                target_peers.remove(config.peer_name)
                if params['parent_peer'] in target_peers: target_peers.remove(params["parent_peer"])
                if target_peers == []: 
                    continue

                for bt in config.bt_list[dt]:
                    tx.cur.execute("SELECT {}_propagates_to_{}({})".format(bt, dt, local_xid))
                tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
                try:
                    delta, *_ = tx.cur.fetchone()
                except Exception as e:
                    if str(e) == "no results to fetch":
                        delta = None
                tx.cur.execute("SELECT public.remove_dummy_{}({})".format(dt, local_xid))

                if delta == None: continue
                delta = json.loads(delta)

                prop_dict[dt] = {}
                prop_dict[dt]['peers'] = target_peers
                prop_dict[dt]['delta'] = delta

                # tx.extend_childs(target_peers)

        except Exception as e:
            if str(e).startswith("the JSON object must be str, bytes or bytearray"):
                print("delta:", delta)
            # tx.reset_childs()
            errors.out_err(e, "BIRDS execution error", out_trace=True)
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, global_xid, params["method"], params['global_params'])
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
        return data_pb2.Response(json_str=json.dumps(res_dic))