import os
import json
from dejima import config
from dejima import dejimautils
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
        self.fetchone_result = None

    # _restore
    def _restore(self):
        if self.locking_method == "frs":
            dejimautils.release_lock_request(self.global_xid) 
        self.tx.abort()
        del config.tx_dict[self.global_xid]
        self._init()

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
        if not lineages:
            print("warn: lineages is empty, canceled global lock")
            return "Ack"
        self.locking_method = "frs"
        result = dejimautils.lock_request(lineages, self.global_xid)
        if result != "Ack":
            self._restore()
            raise errors.GlobalLockNotAvailable("abort during global lock")
        return result

    # execution
    def execute_stmt(self, stmt, max_retry_cnt=0, DEBUG=False):
        try:
            self.fetchone_result = None
            self.tx.cur.execute(stmt)
            if max_retry_cnt:
                result = self.fetchone()
                retry_cnt = 0
                while not result and retry_cnt < max_retry_cnt:
                    self.tx.cur.execute(stmt)
                    result = self.fetchone()
                    retry_cnt += 1
                self.fetchone_result = result
                if retry_cnt:
                    if self.fetchone_result:
                        print(f'"{stmt}": retried {retry_cnt} out of {max_retry_cnt} times to get a result')
                    else:
                        print(f'"{stmt}": failed to fetch a result after trying {retry_cnt} times')
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

    # fetch
    def fetchone(self):
        """Returns:
        - success -> psycopg2.extras.DictRow   ex) [val1, val2, ...]
        - select non-existent record -> None
        - no result (INSERT, UPDATE, DELETE) -> raise psycopg2.ProgrammingError: no results to fetch
        """
        if self.fetchone_result:
            result = self.fetchone_result
            self.fetchone_result = None
        else:
            result = self.tx.cur.fetchone()
        return result
    def fetchall(self):
        """Returns:
        - success -> list   ex) [DictRow, DictRow, ...]
        - select non-existent record -> []
        """
        if self.fetchone_result:
            result = [self.fetchone_result] + self.tx.cur.fetchall()
            self.fetchone_result = None
        else:
            result = self.tx.cur.fetchall()
        return result

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
            result = dejimautils.prop_request(prop_dict, self.global_xid, self.locking_method, self.global_params)
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
        result = "abort"
        if self.status in commit_status_list:
            result = "commit"

        if result == "commit":
            self.tx.commit()
            dejimautils.termination_request("commit", self.global_xid, self.locking_method)
            msg = "commited"
        else:
            self.tx.abort()
            dejimautils.termination_request("abort", self.global_xid, self.locking_method)
            msg = "aborted"
        del config.tx_dict[self.global_xid]

        if DEBUG: print("termination:", msg)
        return msg
