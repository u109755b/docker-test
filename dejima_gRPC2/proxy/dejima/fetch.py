import json
import time
import os
from collections import deque
from opentelemetry import trace
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import errors
from dejima import dejimautils
from dejima import requester
from dejima.transaction import Tx

tracer = trace.get_tracer(__name__)


class Fetch(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("fetch")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)

        params = json.loads(req.json_str)

        global_xid = params['xid']
        if global_xid not in config.tx_dict:
            tx = Tx(global_xid, params["start_time"])
        else:
            tx = config.tx_dict[global_xid]

        # create lock statements
        bt_list = config.dejima_config_dict['base_table'][config.peer_name]
        bt_list = sum(bt_list.values(), [])
        lineage_set = set(params["lineages"])
        lineage_set.discard("dummy")
        lock_stmts = []


        # at a adr peer
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        # if config.peer_name in config.adr_peers:
        is_r_peer = config.get_is_r_peer(list(params["lineages"])[0])
        for lineage in params["lineages"]:
            if config.get_is_r_peer(lineage) != is_r_peer:
                print(f"{os.path.basename(__file__)}: error lineage set")
                raise Exception
        if is_r_peer:
            expansion_lineages = config.countup_request(lineage_set, "read", params["parent_peer"])
            for lineage in expansion_lineages:
                config.is_edge_r_peer[lineage] = False
                config.r_direction[lineage].add(params["parent_peer"])
                config.request_count[lineage] = deque()
            if expansion_lineages:
                res_dic["expansion_data"] = {"peer": config.peer_name, "lineages": expansion_lineages}
            latest_data_dict = {}
            for dt in config.dt_list:
                if dt == "d_customer":
                    lineage_col_name = "c_lineage"   # hardcode (lineage name)
                else:
                    lineage_col_name = "lineage"
                if not lineage_set: break
                conditions = " OR ".join([f"{lineage_col_name} = '{lineage}'" for lineage in lineage_set])
                tx.cur.execute(f"SELECT * FROM {dt} WHERE {conditions} FOR SHARE")
                latest_data = tx.cur.fetchall()
                latest_data_dict[dt] = latest_data
            res_dic["latest_data_dict"] = latest_data_dict
            return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))


        # lock with lineages
        res_dic = {"result": "Nak"}
        res_dic["peer_name"] = config.peer_name

        for bt in bt_list:
            if bt == "customer":
                lineage_col_name = "c_lineage"   # hardcode (lineage name)
            else:
                lineage_col_name = "lineage"
            if not lineage_set: break
            conditions = " OR ".join([f"{lineage_col_name} = '{lineage}'" for lineage in lineage_set])
            lock_stmt = f"SELECT {lineage_col_name} FROM {bt} WHERE {conditions} FOR UPDATE"
            lock_stmts.append(lock_stmt)

        try:
            dejimautils.lock_records(tx, lock_stmts, max_retry_cnt=0, min_miss_cnt=-1, wait_die=True)

        except errors.RecordsNotFound as e:
            print(f"{os.path.basename(__file__)}: global lock failed (Not Found)")
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))


        # propagate latest data from other peers
        res_dic = {"result": "Ack"}
        res_dic["peer_name"] = config.peer_name

        result = requester.fetch_request(params["lineages"], params["xid"], params["start_time"], params["global_params"])
        if "latest_data_dict" not in params["global_params"]:
            return data_pb2.Response(json_str=json.dumps(res_dic))
        latest_data_dict = params["global_params"]["latest_data_dict"]

        local_xid = tx.get_local_xid()
        for dt, latest_data_list in latest_data_dict.items():
            if dt not in config.dt_list: continue
            if type(latest_data_list) is list:
                for latest_data in latest_data_list:
                    lineage = latest_data[-3]
                    if dt == "d_customer":
                        lineage_col_name = "c_lineage"   # hardcode (lineage name)
                    else:
                        lineage_col_name = "lineage"
                    tx.cur.execute(f"DELETE FROM {dt} WHERE {lineage_col_name} = '{lineage}'")
                    values = ", ".join(repr(value) for value in latest_data)
                    tx.cur.execute(f"INSERT INTO {dt} VALUES ({values})")
                tx.cur.execute(f"SELECT {dt}_propagate({local_xid})")
            else:
                stmt = dejimautils.get_execute_stmt(latest_data_list, local_xid)
                tx.cur.execute(stmt)

        # propagate to dejima table
        prop_dict = {}
        for dt in config.dt_list:
            for bt in config.bt_list[dt]:
                tx.cur.execute("SELECT {}_propagates_to_{}({})".format(bt, dt, local_xid))
            tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
            delta, *_ = tx.cur.fetchone()
            tx.cur.execute("SELECT public.remove_dummy_{}({})".format(dt, local_xid))
            if delta == None: continue
            delta = json.loads(delta)
            prop_dict[dt] = delta
        res_dic["latest_data_dict"] = prop_dict

        return data_pb2.Response(json_str=json.dumps(res_dic, default=dejimautils.datetime_converter))
