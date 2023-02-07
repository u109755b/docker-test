import json
import dejimautils
import config
import time
from transaction import Tx

class FRSPropagation(object):
    def __init__(self):
        pass

    def on_post(self, req, resp):
        timestamps = []
        timestamp = []
        timestamp.append(time.perf_counter())
        
        time.sleep(config.SLEEP_MS * 0.001)

        if req.content_length:
            body = req.bounded_stream.read()
            params = json.loads(body)

        global_xid = params['xid']
        max_hop = params['max_hop']
        if max_hop != -1:
            max_hop -= 1
        measure_time = params['measure_time']
        
        # with open('{}/{}.log'.format(config.time_dir, global_xid)) as f:
        #     start_time = int(f.readline())
        # with open('{}/{}.log'.format(config.time_dir, global_xid), mode='a') as f:
        #     elapsed_time = time.perf_counter()-start_time
        #     f.write('start propagation: {}\n'.format(elapsed_time*1000))
        
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
            resp.text = json.dumps({"result": "Nak"})
            print("A propagation loop detected")
            return
        
        # update dejima table and propagate to base tables
        try:
            stmt = dejimautils.convert_to_sql_from_json(params['delta'])
            # additional lock for peers out of lock scope
            if not locked_flag:
                for bt in config.bt_list:
                    # if bt == "customer":
                    #     for delete in params['delta']["deletions"]:
                    #         tx.cur.execute("SELECT * FROM customer WHERE c_w_id={} AND c_d_id={} AND c_id={} FOR UPDATE NOWAIT".format(delete['c_w_id'], delete['c_d_id'], delete['c_id']))
                    # else:
                    #     for delete in params['delta']["deletions"]:
                    #         tx.cur.execute("SELECT * FROM bt WHERE id={} FOR UPDATE NOWAIT".format(delete['id']))
                    timestamp.append(time.perf_counter())
                    for delete in params['delta']["deletions"]:
                        tx.cur.execute("SELECT * FROM bt WHERE v={} FOR UPDATE NOWAIT".format(delete['v']))
                    timestamp.append(time.perf_counter())
            else:
                timestamp.append(time.perf_counter())
                timestamp.append(time.perf_counter())
            tx.cur.execute(stmt)
            timestamp.append(time.perf_counter())
            if max_hop != -1:
                for insert in params['delta']["insertions"]:
                    config.candidate_record_id_list.append(insert['v'])
            if max_hop > 0:
                stmt = dejimautils.prop_to_dt_for_rsab(params['delta'])
                tx.cur.execute(stmt)
        except Exception as e:
            print(e)
            resp.text = json.dumps({"result": "Nak", "info": e.__class__.__name__})
            return

        try: 
            # get local xid
            tx.cur.execute("SELECT txid_current()")
            local_xid, *_ = tx.cur.fetchone()
            timestamp.append(time.perf_counter())

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
            msg = {"result": "Nak"}
            resp.text = json.dumps(msg)
            return
        
        timestamp.append(time.perf_counter())
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, global_xid, "frs", max_hop, measure_time=measure_time)
        else:
            result = "Ack"
        timestamp.append(time.perf_counter())
        
        if result == "Ack" and measure_time == True:
            result = []
        if isinstance(result, list):
            timestamps = result
            timestamps.append(timestamp)
            result = "Ack"
        
        if result != "Ack":
            msg = {"result": "Nak"}
        else:
            msg = {"result": "Ack", "timestamps": timestamps}
        
        # with open('{}/{}.log'.format(config.time_dir, global_xid), mode='a') as f:
        #     elapsed_time = time.perf_counter()-start_time
        #     f.write('end propagation: {}\n'.format(elapsed_time*1000))
        
        resp.text = json.dumps(msg)
        return