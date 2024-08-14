import os
import json
from datetime import datetime
import dejima.status
from dejima import config
from dejima import dejimautils
from dejima import adrutils
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
        if config.adr_mode:
            adrutils.countup_request(lineages, "update", config.peer_name)
        result = requester.lock_request(lineages, self.global_xid, self.tx.start_time)
        if result != "Ack":
            self._restore()
            raise errors.GlobalLockNotAvailable("abort during global lock")
        return result

    # fetch global records
    def fetch_global(self, lineages):
        if not lineages: return "Ack"
        adrutils.countup_request(lineages, "read", config.peer_name)
        lineages = [lineage for lineage in lineages if not adrutils.get_is_r_peer(lineage)]
        if not lineages: return "Ack"

        # check latest timestamps
        global_params = {}
        result = requester.check_latest_request(lineages, self.global_xid, self.tx.start_time, global_params)
        if result != "Ack":
            self._restore()
            raise errors.GlobalLockNotAvailable("abort during global fetch")
        self.tx.extend_childs(global_params["peer_names"])

        # check which is old data
        lineages = []
        for lineage, latest_timestamp in global_params["latest_timestamps"].items():
            if not latest_timestamp:
                continue
            for dt in config.dt_list:
                lineage_col_name, condition =  dejimautils.get_where_condition(dt, lineage)
                self.execute_stmt(f"SELECT updated_at FROM {dt} WHERE {condition}")
                local_timestamp, *_ = self.fetchone()
                if not local_timestamp: continue
                latest_timestamp = datetime.fromisoformat(latest_timestamp)
                if local_timestamp != latest_timestamp:
                    lineages.append(lineage)
                break

        if not lineages: return "Ack"

        # lock for update
        try:
            dejimautils.lock_with_lineages(self.tx, lineages, for_what="UPDATE")
        except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
            return "Nak"

        # propagate latest data from other peers
        global_params = {}
        result = requester.fetch_request(lineages, self.global_xid, self.tx.start_time, global_params)
        if result != "Ack":
            return "Nak"
        if "latest_data_dict" not in global_params: return result

        # fetch to local
        local_xid = self.tx.get_local_xid()
        dejimautils.execute_fetch(local_xid, global_params["latest_data_dict"], self.execute_stmt)

        # propagate to dejima table
        for dt in config.dt_list:
            dejimautils.propagate_to_dt(dt, local_xid, self.tx.cur)
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
                target_peers = [peer for peer in config.dejima_config_dict["dejima_table"][dt] 
                                if peer != config.peer_name]
                if not target_peers: continue

                delta = dejimautils.propagate_to_dt(dt, local_xid, self.tx.cur)
                if not delta: continue

                prop_dict[dt] = {"peers": target_peers, "delta": delta}

                lineages = [insertion["lineage"] for insertion in delta["insertions"]]
                adrutils.init_adr_setting_if_not(lineages)

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
    def propagate(self, global_params={}, is_load=False, DEBUG=False):
        self.global_params = global_params
        if is_load: self.global_params["is_load"] = True
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
