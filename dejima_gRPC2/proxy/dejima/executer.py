import os
import json
import time
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
        self.prop_num = 0
        self.first_r_peer = {}

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

    # fetch global records
    def fetch_global(self, lineages):
        if not lineages: return "Ack"
        lineages = set(lineages) - {"dummy"}
        for lineage in lineages:
            if adrutils.get_is_r_peer(lineage): adrutils.read_req_num[lineage] += 1
        lineages = [lineage for lineage in lineages if not adrutils.get_is_r_peer(lineage)]
        if not lineages: return "Ack"

        # check local timestamps
        global_params = {}
        global_params["prop_num"] = self.prop_num
        global_params["timestamps"] = {lineage: dejimautils.get_timestamp(self.tx, lineage, to_isoformat=True)
                                       for lineage in lineages}
        result = requester.check_latest_request(lineages, self.global_xid, self.tx.start_time, global_params)
        if result != "Ack":
            self._restore()
            raise errors.GlobalLockNotAvailable("abort during global fetch")
        self.tx.extend_childs(global_params["peer_names"], self.prop_num)
        self.tx.extend_childs_all(global_params["all_peers"])

        lineages = global_params["fetch_lineages"]
        if not lineages: return "Ack"

        # lock for update
        timestamp = []
        timestamp.append(time.perf_counter())   # 0
        try:
            dejimautils.lock_with_lineages(self.tx, lineages, for_what="UPDATE")
        except (errors.RecordsNotFound, errors.LockNotAvailable) as e:
            return "Nak"
        timestamp.append(time.perf_counter())   # 1

        # propagate latest data from other peers
        global_params = {}
        global_params["prop_num"] = self.prop_num
        result = requester.fetch_request(lineages, self.global_xid, self.tx.start_time, global_params)
        self.prop_num += 1
        if result != "Ack":
            return "Nak"

        # fetch to local
        timestamp.append(time.perf_counter())   # 2
        local_xid = self.tx.get_local_xid()
        latest_data_dict = global_params["latest_data_dict"]
        dejimautils.execute_fetch(self.execute_stmt, local_xid, latest_data_dict)

        # propagate to dejima table
        for dt in config.dt_list:
            dejimautils.propagate_to_dt(self.tx, dt, local_xid)

        timestamp.append(time.perf_counter())   # 3
        adrutils.add_read_prop_time(timestamp[1]-timestamp[0] + timestamp[3]-timestamp[2])
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
        insertion_lineages = set()
        deletion_lineages = set()
        # refresh dejima table
        try:
            local_xid = self.tx.get_local_xid()
            for dt in config.dt_list:
                target_peers = [peer for peer in config.dejima_config_dict["dejima_table"][dt] 
                                if peer != config.peer_name]
                if not target_peers: continue

                delta = dejimautils.propagate_to_dt(self.tx, dt, local_xid)
                if not delta: continue

                prop_dict[dt] = {"peers": target_peers, "delta": delta}

                insertion_lineages |= set([insertion["lineage"] for insertion in delta.get("insertions", [])])
                deletion_lineages |= set([deletions["lineage"] for deletions in delta.get("deletions", [])])
            adrutils.init_adr_setting_if_not(insertion_lineages)

        except Exception as e:
            self._restore()
            errors.out_err(e, "BIRDS execution error", out_trace=True)
            raise

        update_lineages = insertion_lineages & deletion_lineages
        return prop_dict, update_lineages

    # propagate to other peers
    def propagate_other_peer(self, prop_dict, update_lineages, DEBUG=False):
        result = "Ack"
        if prop_dict != {}:
            self.global_params["prop_num"] = self.prop_num
            self.global_params["update_lineages"] = list(update_lineages).copy()
            self.global_params["first_r_peer"] = {}
            self.global_params["parent_peer"] = config.peer_name
            result = requester.prop_request(prop_dict, self.global_xid, self.tx.start_time, self.locking_method, self.global_params)
            self.tx.extend_childs(self.global_params["peer_names"], self.prop_num)
            self.tx.extend_childs_all(self.global_params["all_peers"])
            self.prop_num += 1

            if result == "Ack" and config.adr_mode and config.change_r:
                self.first_r_peer.update(self.global_params["first_r_peer"])

                for lineage in update_lineages:
                    # update_req_num_total = self.global_params["update_req_num_total"][lineage]+1
                    if self.global_params["update_req_num_total"][lineage]+1 < config.update_num_per_test: continue

                    # get_leaf_distance
                    global_params = {}
                    requester.ec_test("get_leaf_distance", lineage, global_params)
                    peers = global_params["peers"]
                    edges = global_params["edges"]
                    peers[self.first_r_peer[lineage]]["update_req_num"] += 1
                    # for peer_name in peers:
                    #     peer = peers[peer_name]
                    #     print(f"{peer_name}: {peer["is_r"]} {peer['update_prop_time']}, {peer['read_prop_time']}, {update_req_num_total}, {peer['update_req_num']}, {peer['read_req_num']}, {peer['fetch_num']}")

                    # get_center_peer
                    global_params = {}
                    requester.ec_test("get_center_peer", lineage, global_params)
                    center_peer_name, radius = global_params["center_peer_info"]
                    if radius == float("inf"): continue

                    # expand_contract
                    ec_info = adrutils.ec_test(peers, edges, center_peer_name)
                    global_params = {"ec_info": ec_info}
                    requester.ec_test("expand_contract", lineage, global_params)
                    self.first_r_peer = {}

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
        prop_dict, update_lineages = self.propagate_dejima_table()
        result = self.propagate_other_peer(prop_dict, update_lineages, DEBUG)
        return result


    # terminate
    def terminate(self, DEBUG=False):
        commit_status_list = {}
        commit_status_list["2pl"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list["frs"] = [self.status_clean, self.status_dirty, self.status_proped]
        commit_status_list = commit_status_list[self.locking_method]
        global_params = {"first_r_peer": self.first_r_peer}

        if self.status in commit_status_list:
            self.tx.commit()
            requester.termination_request("commit", self.global_xid, global_params)
            result = dejima.status.COMMITTED
            msg = "committed"
        else:
            self.tx.abort()
            requester.termination_request("abort", self.global_xid, global_params)
            result = dejima.status.ABORTED
            msg = "aborted"
        self.tx.close()

        if DEBUG: print("termination:", msg)
        return result
