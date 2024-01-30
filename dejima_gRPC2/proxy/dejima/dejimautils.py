import json
import threading
import uuid
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.context import attach, detach, set_value
import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config

if config.trace_enabled:
    GrpcInstrumentorClient().instrument()
tracer = trace.get_tracer(__name__)

def get_unique_id():
    return config.peer_name + '-' + str(uuid.uuid4())

def lock_request(lineages, global_xid):
    with tracer.start_as_current_span("lock_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        lock = threading.Lock()
        for peer in config.target_peers:
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.LockStub
            data = {
                "xid": global_xid,
                "lineages": lineages
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)
        
        for thread in thread_list:
            thread.start()
        
        for thread in thread_list:
            thread.join()
        
        if all(results):
            return "Ack"
        else:
            return "Nak"

@tracer.start_as_current_span("release_request")
def release_lock_request(global_xid):
    thread_list = []
    results = []
    lock = threading.Lock()
    for peer in config.target_peers:
        peer_address = config.dejima_config_dict['peer_address'][peer]
        service_stub = data_pb2_grpc.UnlockStub
        data = {
            "xid": global_xid
        }
        req = data_pb2.Request(json_str=json.dumps(data))
        args = ([peer_address, service_stub, req, results, lock])
        thread = threading.Thread(target=base_request, args=args)
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    
    if all(results):
        return "Ack"
    else:
        return "Nak"

def prop_request(arg_dict, global_xid, method, global_params={}):
    with tracer.start_as_current_span("prop_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        params = {}
        params["peer_name"] = [None]
        if "max_hop" in global_params: params["max_hop"] = [0]
        if "timestamps" in global_params: params["timestamps"] = [[]]
        lock = threading.Lock()
        for dt in arg_dict.keys():
            for peer in arg_dict[dt]['peers']:
                peer_address = config.dejima_config_dict['peer_address'][peer]
                service_stub = data_pb2_grpc.PropagationStub
                data = {
                    "xid": global_xid,
                    "method": method,
                    "dejima_table": dt,
                    "delta": arg_dict[dt]['delta'],
                    "parent_peer": config.peer_name,
                    "global_params": global_params,
                }
                req = data_pb2.Request(json_str=json.dumps(data))
                args = ([peer_address, service_stub, req, results, lock, ctx, params])
                thread = threading.Thread(target=base_request, args=args)
                thread_list.append(thread)

            for thread in thread_list:
                thread.start()

            for thread in thread_list:
                thread.join()

            if not all(results): break
            thread_list = []

        peer_names = set(params["peer_name"])
        peer_names.remove(None)
        global_params["peer_names"] = list(peer_names)
        if "max_hop" in global_params:
            if config.hop_mode: global_params["max_hop"] = max(params["max_hop"]) + 1
            else: global_params["max_hop"] = sum(params["max_hop"]) + 1
        if "timestamps" in global_params:
            global_params["timestamps"] = max(params["timestamps"], key=len)
        if all(results):
            return "Ack"
        else:
            return "Nak"

def termination_request(result, current_xid, method):
    with tracer.start_as_current_span("termination_request") as span:
        ctx = set_value("current_span", span)
        thread_list = []
        results = []
        lock = threading.Lock()
        peers = config.tx_dict[current_xid].child_peers
        for peer in peers:
            peer_address = config.dejima_config_dict['peer_address'][peer]
            service_stub = data_pb2_grpc.TerminationStub
            data = {
                "xid": current_xid,
                "method": method,
                "result": result
            }
            req = data_pb2.Request(json_str=json.dumps(data))
            args = ([peer_address, service_stub, req, results, lock, ctx])
            thread = threading.Thread(target=base_request, args=args)
            thread_list.append(thread)
        
        for thread in thread_list:
            thread.start()
        
        for thread in thread_list:
            thread.join()
        
        if all(results):
            return "Ack"
        else:
            return "Nak"

def base_request(peer_address, service_stub, req, results, lock, ctx=None, params={}):
    try:
        if ctx: token = attach(ctx)
        
        # with tracer.start_as_current_span("base_request") as span:
        if peer_address not in config.channels:
            config.channels[peer_address] = grpc.insecure_channel(peer_address)
        stub = service_stub(config.channels[peer_address])
        res = stub.on_post(req)
        res_dic = json.loads(res.json_str)
        # with lock:
        if res_dic['result'] == "Ack":
            results.append(True)
        else:
            results.append(False)
        if "peer_name" in res_dic:
            params["peer_name"].append(res_dic["peer_name"])
        if "max_hop" in res_dic:
            params["max_hop"].append(res_dic["max_hop"])
        if "timestamps" in res_dic:
            params["timestamps"].append(res_dic["timestamps"])

        if ctx: detach(token)
    except Exception as e:
        print("base_request:", e)
        results.append(False)
        if ctx: detach(token)


def get_lock_stmts(json_data):
    lock_stmts = []
    json_dict = json_data
    for delete in json_dict["deletions"]:
        where = []
        for column, value in delete.items():
            if column=='txid': continue
            if not value and value != 0: continue   # NULL
            if type(value) is str:
                where.append(f"{column}='{value}'")
            else:
                where.append(f"{column}={value}")
        where = " AND ".join(where)
        lock_stmts.append("SELECT * FROM {} WHERE {} FOR UPDATE NOWAIT".format(json_dict["view"], where))
    return lock_stmts

def get_execute_stmt(json_data, local_xid):
    sql_statements = []
    json_dict = json_data

    for delete in json_dict["deletions"]:
        where = []
        for column, value in delete.items():
            if column=='txid': continue
            if not value and value != 0: continue   # NULL
            if type(value) is str:
                where.append(f"{column}='{value}'")
            else:
                where.append(f"{column}={value}")
        where = " AND ".join(where)
        sql_statements.append("DELETE FROM {} WHERE {} RETURNING true".format(json_dict["view"], where))

    for insert in json_dict["insertions"]:
        columns = []
        values = []
        for column, value in insert.items():
            if column=='txid': continue
            columns.append(f"{column}")
            if not value and value != 0:
                values.append("NULL")
            elif type(value) is str:
                values.append(f"'{value}'")
            else:
                values.append(f"{value}")
        columns = "({})".format(", ".join(columns))
        values = "({})".format(", ".join(values))
        sql_statements.append("INSERT INTO {} {} VALUES {} RETURNING true".format(json_dict["view"], columns, values))
        
    update_stmts = []
    for i, stmt in enumerate(sql_statements):
        update_stmts.append("updated{} AS ({})".format(i, stmt))
    # print(local_xid)
    update_stmts.append("prop_to_bt AS (SELECT {}_propagate({}))".format(json_dict["view"], local_xid))
    update_stmts = "WITH " + ", ".join(update_stmts)
    union_stmts = []
    for i, _ in enumerate(sql_statements):
        union_stmts.append("SELECT * FROM updated{}".format(i))
    union_stmts.append("SELECT * FROM prop_to_bt")
    union_stmts = " UNION ".join(union_stmts)
    execute_stmt = update_stmts + union_stmts

    return execute_stmt