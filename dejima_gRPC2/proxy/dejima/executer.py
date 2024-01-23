import json
import config
from transaction import Tx
import dejimautils
from benchmark.tpcc import tpccutils

class Executer:
    def __init__(self):
        self.status_clean = "clean"
        self.status_dirty = "dirty"
        self.status_proped = "proped"
        self.status_error = "error"
        self._init()

    # _init
    def _init(self):
        self.locking_method = "2pl"
        self.status = self.status_clean
    # _restore
    def _restore(self):
        if self.locking_method == "frs":
            dejimautils.release_lock_request(self.global_xid) 
        self.tx.abort()
        del config.tx_dict[self.global_xid]
        self.init()

    # create new tx
    def create_tx(self):
        self.global_xid = dejimautils.get_unique_id()
        self.tx = Tx(self.global_xid)
        config.tx_dict[self.global_xid] = self.tx

    # set tx
    def set_tx(self, global_xid):
        self.global_xid = global_xid
        if self.global_xid in config.tx_dict:
            self.tx = config.tx_dict[global_xid]
        else:
            self.tx = Tx(self.global_xid)
            config.tx_dict[self.global_xid] = self.tx

    # lock global records
    def lock_global(self, lineages):
        self.locking_method = "frs"
        result = dejimautils.lock_request(lineages, self.global_xid)

    # execution
    def execute_stmt(self, stmt):
        try:
            self.tx.cur.execute(stmt)
        except Exception as e:
            print("abort during local execution: ", e)
            self._restore()
            raise Exception("local execution error")
        self.status = self.status_dirty

    # propagate
    def propagate(self, DEBUG=False):
        prop_dict = {}
        # refresh dejima table
        try:
            self.tx.cur.execute("SELECT txid_current()")
            local_xid, *_ = self.tx.cur.fetchone()
            for dt in config.dt_list:
                target_peers = list(config.dejima_config_dict['dejima_table'][dt])
                target_peers.remove(config.peer_name)
                if target_peers == []: continue

                for bt in config.bt_list[dt]:
                    self.tx.cur.execute("SELECT {}_propagate_updates_to_{}()".format(bt, dt))
                self.tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
                delta, *_ = self.tx.cur.fetchone()

                if delta == None: continue
                delta = json.loads(delta)

                prop_dict[dt] = {}
                prop_dict[dt]['peers'] = target_peers
                prop_dict[dt]['delta'] = delta

                self.tx.extend_childs(target_peers)

        except Exception as e:
            print('error during BIRDS: ', e)
            self._restore()
            raise Exception("BIRDS execution error")

        # propagate to other peers
        result = "Ack"
        if prop_dict != {}:
            result = dejimautils.prop_request(prop_dict, self.global_xid, self.locking_method)

        if result == "Ack" and self.status != self.status_error:
            self.status = self.status_proped
        else:
            self.status = self.status_error

        if DEBUG: print("propagation:", result)
        return result


    # terminate
    def terminate(self, DEBUG=False):
        commit_status_list = {}
        commit_status_list["2pl"] = [self.status_clean, self.status_dirty]
        commit_status_list["frs"] = [self.status_clean, self.status_proped]
        commit_status_list = commit_status_list[self.locking_method]
        result = "abort"
        if self.status in commit_status_list:
            result = "commit"

        if result == "commit":
            self.tx.commit()
            dejimautils.termination_request("commit", self.global_xid, "frs")
            msg = "commited"
        else:
            self.tx.abort()
            dejimautils.termination_request("abort", self.global_xid, "frs")
            msg = "aborted"
        del config.tx_dict[self.global_xid]

        if DEBUG: print("termination:", msg)
        return msg
