import json
import dejimautils
import config
import time
from transaction import Tx
import data_pb2
import data_pb2_grpc

# class TPLPropagation(object):
class TPLPropagation(data_pb2_grpc.TPLPropagationServicer):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        timestamp = []
        timestamp.append(time.perf_counter())   # 0
        
        time.sleep(config.SLEEP_MS * 0.001)

        # if req.content_length:
        #     body = req.bounded_stream.read()
        #     params = json.loads(body)
        params = json.loads(req.json_str)

        global_xid = params['xid']
        tx = Tx(global_xid)
        config.tx_dict[global_xid] = tx

        if tx.propagation_cnt == 0:
            tx.propagation_cnt += 1
        else:
            print("A propagation loop detected")
            # resp.text = json.dumps({"result": "Nak"})
            # return
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        # prepare lock stmts
        stmt = dejimautils.convert_to_sql_from_json(params['delta'])
        lineages = []
        lock_stmts = []
        for bt in config.bt_list:
            if bt == "customer":
                for delete in params['delta']["deletions"]:
                    lineage = config.lock_management.get_tpcc_lineage('customer', delete['c_w_id'], delete['c_d_id'], delete['c_id'])
                    lineages.append(lineage)
                    lock_stmts.append("SELECT * FROM customer WHERE c_w_id={} AND c_d_id={} AND c_id={} FOR UPDATE NOWAIT".format(delete['c_w_id'], delete['c_d_id'], delete['c_id']))
            else:
                for delete in params['delta']["deletions"]:
                    lock_stmts.append("SELECT * FROM bt WHERE id={} FOR UPDATE NOWAIT".format(delete['id']))

        # update dejima table and propagate to base tables
        try:
            for lineage, lock_stmt in zip(lineages, lock_stmts):
                if config.plock_mode: config.lock_management.lock(global_xid, lineage)
                tx.cur.execute(lock_stmt)
            timestamp.append(time.perf_counter())   # 1
            tx.cur.execute(stmt)
            timestamp.append(time.perf_counter())   # 2
        except Exception as e:
            # resp.text = json.dumps({"result": "Nak", "info": e.__class__.__name__})
            # return
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
            # msg = {"result": "Nak"}
            # resp.text = json.dumps(msg)
            # return
            res_dic = {"result": "Nak"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        timestamp.append(time.perf_counter())   # 3
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, global_xid, "2pl", params['global_params'])
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
        # resp.text = json.dumps(msg)
        # return
        return data_pb2.Response(json_str=json.dumps(res_dic))