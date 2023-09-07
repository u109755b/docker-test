import json
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import threading
import requests
import uuid
import config

def get_unique_id():
    return config.peer_name + '-' + str(uuid.uuid4())

def lock_request(lineages, global_xid):
    thread_list = []
    results = []
    lock = threading.Lock()
    for peer in config.target_peers:
        url = "http://{}/_lock".format(config.dejima_config_dict['peer_address'][peer])
        data = {
            "xid": global_xid,
            "lineages": lineages
        }
        thread = threading.Thread(target=base_request, args=([url, data, results, lock]))
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    
    if all(results):
        return "Ack"
    else:
        return "Nak"

def release_lock_request(global_xid):
    thread_list = []
    results = []
    lock = threading.Lock()
    for peer in config.target_peers:
        url = "http://{}/_unlock".format(config.dejima_config_dict['peer_address'][peer])
        data = {
            "xid": global_xid
        }
        thread = threading.Thread(target=base_request, args=([url, data, results, lock]))
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    
    if all(results):
        return "Ack"
    else:
        return "Nak"

def prop_request(arg_dict, global_xid, method):
    thread_list = []
    results = []
    lock = threading.Lock()
    for dt in arg_dict.keys():
        for peer in arg_dict[dt]['peers']:
            data = {
                "xid": global_xid,
                "dejima_table": dt,
                "delta": arg_dict[dt]['delta'],
                "parent_peer": config.peer_name
            }
            url = "http://{}/{}/_propagate".format(config.dejima_config_dict['peer_address'][peer], method)
            thread = threading.Thread(target=base_request, args=([url, data, results, lock]))
            thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    
    if all(results):
        return "Ack"
    else:
        return "Nak"

def termination_request(result, current_xid, method):
    thread_list = []
    results = []
    lock = threading.Lock()
    peers = config.tx_dict[current_xid].child_peers
    for peer in peers:
        data = {
            "xid": current_xid,
            "result": result
        }
        url = "http://{}/{}/_terminate".format(config.dejima_config_dict['peer_address'][peer], method)
        thread = threading.Thread(target=base_request, args=([url, data, results, lock]))
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    
    if all(results):
        return "Ack"
    else:
        return "Nak"

def base_request(url, data, results, lock):
    try:
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json.dumps(data), headers=headers)
        with lock:
            if res.json()['result'] == "Ack":
                results.append(True)
            else:
                results.append(False)
    except Exception as e:
        print(e)
        results.append(False)

def convert_to_sql_from_json(json_data):
    # arg : json_data from other peer
    # output : view name(str) , sql statements for view(str)
    sql_statements = []
    json_dict = json_data
    # json_dict = json.loads(json_data)

    for delete in json_dict["deletions"]:
        where = ""
        for column, value in delete.items():
            if not value and value != 0: continue
            if column=='txid': continue
            if type(value) is str:
                #value=value.strip() # Note: value contains strange Tabs
                where += "{}='{}' AND ".format(column, value)
            else:
                where += "{}={} AND ".format(column, value)
        where = where[0:-4]
        sql_statements.append("DELETE FROM {} WHERE {} RETURNING true".format(json_dict["view"], where))

    for insert in json_dict["insertions"]:
        columns = "("
        values = "("
        for column, value in insert.items():
            if column=='txid': continue
            columns += "{}, ".format(column)
            if not value and value != 0:
                values += "NULL, "
            elif type(value) is str:
                #value=value.strip() # Note: value contains strange Tabs
                values += "'{}', ".format(value)
            else:
                values += "{}, ".format(value)
        columns = columns[0:-2] + ")"
        values = values[0:-2] + ")"
        sql_statements.append("INSERT INTO {} {} VALUES {} RETURNING true".format(json_dict["view"], columns, values))

    ret_stmt = ""
    for i, stmt in enumerate(sql_statements):
        if i == 0:
            ret_stmt = "WITH updated{}".format(i) + " AS ({})".format(stmt)
        else:
            ret_stmt += ", updated{}".format(i) + " AS ({})".format(stmt)
    ret_stmt += ", prop_to_bt AS (SELECT {}_propagate_updates())".format(json_dict["view"])
    union_stmts = []
    for i, _ in enumerate(sql_statements):
        union_stmts.append("SELECT * FROM updated{}".format(i))
    union_stmts.append("SELECT * FROM prop_to_bt")
    ret_stmt += " UNION ".join(union_stmts)

    return ret_stmt

# ----- get table names -----
def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                yield from extract_from_part(item)
            elif item.ttype is Keyword:
                return
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True

def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, Identifier):
            yield item.get_name()
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        elif item.ttype is Keyword:
            yield item.value

def extract_tables(sql):
    stream = extract_from_part(sqlparse.parse(sql)[0])
    return list(extract_table_identifiers(stream))
