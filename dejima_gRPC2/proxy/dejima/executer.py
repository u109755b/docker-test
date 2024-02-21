import os
import json
import dejima.status
from dejima import config
from dejima import dejimautils
from dejima import requester
from dejima import errors
from dejima.transaction import Tx

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
            requester.release_lock_request(self.global_xid) 
        self.tx.abort()
        self.tx.close()
        self._init()

    # create new tx
    def create_tx(self, start_time=None):
        self.global_xid = dejimautils.get_unique_id()
        self.tx = Tx(self.global_xid, start_time)

    # set tx
    def set_tx(self, global_xid, start_time):
        self.global_xid = global_xid
        if self.global_xid in config.tx_dict:
            self.tx = config.tx_dict[global_xid]
        else:
            self.tx = Tx(self.global_xid, start_time)

    # lock global records
    def lock_global(self, lineages):
        if not lineages:
            print("warn: lineages is empty, canceled global lock")
            return "Ack"
        self.locking_method = "frs"
        result = requester.lock_request(lineages, self.global_xid, self.tx.start_time)
        if result != "Ack":
            self._restore()
            raise errors.GlobalLockNotAvailable("abort during global lock")
        return result

    # execution
    def execute_stmt(self, stmt, max_retry_cnt=0, DEBUG=False):
        try:
            self.tx.execute(stmt, max_retry_cnt)
        except errors.LockNotAvailable as e:
            if DEBUG: print(f"{os.path.basename(__file__)}: local lock failed")
            self._restore()
            raise errors.LocalLockNotAvailable("abort during local lock")
        except errors.SyntaxError as e:
            errors.out_err(e, "systax error")
            self._restore()
            raise
        except Exception as e:
            errors.out_err(e, "abort during local execution", out_trace=True)
            self._restore()
            raise
        self.status = self.status_dirty

    # fetchone
    def fetchone(self):
        return self.tx.fetchone()

    # fetchall
    def fetchall(self):
        return self.tx.fetchall()

    # propagate to dejima table
    def propagate_dejima_table(self):
        prop_dict = {}
        # refresh dejima table
        try:
            local_xid = self.tx.get_local_xid()
            for dt in config.dt_list:
                target_peers = list(config.dejima_config_dict['dejima_table'][dt])
                target_peers.remove(config.peer_name)
                if target_peers == []: continue

                for bt in config.bt_list[dt]:
                    self.tx.cur.execute("SELECT {}_propagates_to_{}({})".format(bt, dt, local_xid))
                self.tx.cur.execute("SELECT public.{}_get_detected_update_data({})".format(dt, local_xid))
                delta, *_ = self.tx.cur.fetchone()
                self.tx.cur.execute("SELECT public.remove_dummy_{}({})".format(dt, local_xid))

                if delta == None: continue
                delta = json.loads(delta)

                prop_dict[dt] = {}
                prop_dict[dt]['peers'] = target_peers
                prop_dict[dt]['delta'] = delta

        except Exception as e:
            self._restore()
            errors.out_err(e, "BIRDS execution error", out_trace=True)
            raise

        return prop_dict

    # propagate to other peers
    def propagate_other_peer(self, prop_dict, DEBUG=False):
        result = "Ack"
        if prop_dict != {}:
            result = requester.prop_request(prop_dict, self.global_xid, self.tx.start_time, self.locking_method, self.global_params)
            self.tx.extend_childs(self.global_params["peer_names"])

        if result == "Ack" and self.status != self.status_error:
            self.status = self.status_proped
        else:
            self.status = self.status_error

        if DEBUG: print("propagation:", result)
        return result

    # propagation
    def propagate(self, global_params={}, DEBUG=False):
        self.global_params = global_params
        prop_dict = self.propagate_dejima_table()
        result = self.propagate_other_peer(prop_dict, DEBUG)
        return result


    # terminate
    def terminate(self, DEBUG=False):
        commit_status_list = {}
        commit_status_list["2pl"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list["frs"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list = commit_status_list[self.locking_method]

        if self.status in commit_status_list:
            self.tx.commit()
            requester.termination_request("commit", self.global_xid, self.locking_method)
            result = dejima.status.COMMITTED
            msg = "committed"
        else:
            self.tx.abort()
            requester.termination_request("abort", self.global_xid, self.locking_method)
            result = dejima.status.ABORTED
            msg = "aborted"
        self.tx.close()

        if DEBUG: print("termination:", msg)
        return result
