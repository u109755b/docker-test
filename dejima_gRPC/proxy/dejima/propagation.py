import json
import time
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from transaction import Tx
import config
import dejimautils

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
            tx = config.tx_dict[global_xid]
            locked_flag = True
        else:
            tx = Tx(global_xid)
            config.tx_dict[global_xid] = tx
            locked_flag = False

        if tx.propagation_cnt == 0:
            tx.propagation_cnt += 1
        else:
            print("A propagation loop detected")
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        # update dejima table and propagate to base tables
        try:
            # additional lock for peers out of lock scope
            if not locked_flag:
                lock_stmts = dejimautils.get_lock_stmts(params['delta'])
                for lock_stmt in lock_stmts:
                    tx.cur.execute(lock_stmt)
            timestamp.append(time.perf_counter())   # 1

            # execute stmt
            stmt = dejimautils.get_execute_stmt(params['delta'])
            tx.cur.execute(stmt)
            timestamp.append(time.perf_counter())   # 2

        except Exception as e:
            res_dic = {"result": "Nak", "info": e.__class__.__name__}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        try: 
            # get local xid
            tx.cur.execute("SELECT txid_current()")
            local_xid, *_ = tx.cur.fetchone()

            # propagation
            updated_dt = params['delta']['view'].split('.')[1]
            prop_dict = {}
            for dt in config.dt_list:
                if dt == updated_dt: continue
                target_peers = list(config.dejima_config_dict['dejima_table'][dt])
                target_peers.remove(config.peer_name)
                if params['parent_peer'] in target_peers: target_peers.remove(params["parent_peer"])
                if target_peers == []: 
                    continue

                for bt in config.bt_list:
                    tx.cur.execute("SELECT {}_propagate_updates_to_{}()".format(bt, dt))
                tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
                delta, *_ = tx.cur.fetchone()

                if delta == None: continue
                delta = json.loads(delta)

                prop_dict[dt] = {}
                prop_dict[dt]['peers'] = target_peers
                prop_dict[dt]['delta'] = delta

                tx.extend_childs(target_peers)

        except Exception as e:
            print(e)
            tx.reset_childs()
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, global_xid, params["method"], params['global_params'])
        else:
            result = "Ack"
        timestamp.append(time.perf_counter())   # 4

        if result != "Ack":
            res_dic = {"result": "Nak"}
        else:
            res_dic = {"result": "Ack"}

        if "max_hop" in params["global_params"]:
            res_dic["max_hop"] = params["global_params"]["max_hop"]
        if "timestamps" in params["global_params"] and result == "Ack":
            res_dic["timestamps"] = params["global_params"]["timestamps"]
            res_dic["timestamps"].append(timestamp)
        return data_pb2.Response(json_str=json.dumps(res_dic))