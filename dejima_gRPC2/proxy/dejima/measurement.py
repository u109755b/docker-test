import time
import threading
from collections import defaultdict
from dejima import utils

# TimestampManagement
# measure each time taking process

# TimeMeasurement
# measure arbitrary time

# ResultMeasurement
# measure result time

class TimestampManagement:
    def __init__(self):
        self.duration_time = {'lock': 0, 'base_update': 0, 'prop_view_0': 0, 'view_update': 0, 'prop_view_k': 0, 'communication': 0, 'commit': 0}
        self.data_num = {'lock': 0, 'base_update': 0, 'prop_view_0': 0, 'view_update': 0, 'prop_view_k': 0, 'communication': 0, 'commit': 0}

    def add_duration_time(self, time_name, duration_time):
        self.duration_time[time_name] += duration_time
        self.data_num[time_name] += 1

    def add_timestamps(self, timestamps):
        timestamps = list(reversed(timestamps))
        self.add_duration_time("commit", timestamps[0][-1]-timestamps[0][-2])
        timestamps[0].pop()
        for i, timestamp in enumerate(timestamps):
            self.add_duration_time("lock", timestamp[1]-timestamp[0])
            if i == 0:
                self.add_duration_time('base_update', timestamp[2]-timestamp[1])
                self.add_duration_time('prop_view_0', timestamp[3]-timestamp[2])
            else:
                self.add_duration_time('view_update', timestamp[2]-timestamp[1])
                self.add_duration_time('prop_view_k', timestamp[3]-timestamp[2])
            if i != len(timestamps)-1:
                duration_time = (timestamps[i+1][0]-timestamps[i][-2]) + (timestamps[i][-1]-timestamps[i+1][-1])
                self.add_duration_time('communication', duration_time)

    def get_result(self, display=False):
        avg_ms = lambda x, y: utils.divide(1000*x, y)
        result = utils.general_2obj_func(self.duration_time, self.data_num, avg_ms)
        if display == True: print(utils.general_round2(result), end='[ms]\n')
        return result


class TimeMeasurement:
    def init(self):
        self.start_time = {}
        self.total_duration_time = {}
        self.data_num = {}
        self.plock = threading.Lock()

    def __init__(self):
        self.init()

    def start_timer(self, time_type, global_xid, s_time=None):
        if time_type not in self.start_time:
            self.start_time[time_type] = {}
        if global_xid not in self.start_time[time_type]:
            self.start_time[time_type][global_xid] = []
        if s_time is None:
            s_time = time.perf_counter()
        self.start_time[time_type][global_xid].append(s_time)

    def stop_timer(self, time_type, global_xid, save=True):
        s_time = self.start_time[time_type][global_xid].pop()
        e_time = time.perf_counter()
        if not self.start_time[time_type][global_xid]:
            del self.start_time[time_type][global_xid]
        if save is False:
            return
        if time_type not in self.total_duration_time:
            self.total_duration_time[time_type] = []
            self.data_num[time_type] = []
        self.total_duration_time[time_type].append(e_time - s_time)
        self.data_num[time_type].append(1)

    def get_result(self, display=False):
        result = {}
        with self.plock:
            for time_type, td_time in self.total_duration_time.items():
                total_time = sum(self.total_duration_time[time_type])
                total_num = sum(self.data_num[time_type])
                self.total_duration_time[time_type] = [total_time]
                self.data_num[time_type] = [total_num]
                if time_type == 'lock_process': result[time_type] = 1000*total_time
                else: result[time_type] = 1000*total_time / total_num
        if not result: return {}
        if display == True: print(utils.general_round2(result), end='[ms]\n')
        return result
time_measurement = TimeMeasurement()


class ResultMeasurement:
    def __init__(self):
        # コミット数 (Updateコミット数+Readコミット数)  コミットの合計時間 (Updateコミットの合計時間+Readコミットの合計時間)
        # アボート数 (Globalアボート数+Localアボート数)  アボートの合計時間 (Globalアボートの合計時間+Localアボートの合計時間)
        self.start_time = 0
        self.tx_type = None

        self.update_commit_num = 0
        self.read_commit_num = 0
        self.tx_commit_num = defaultdict(lambda: 0)
        self.update_commit_time = 0
        self.read_commit_time = 0
        self.tx_commit_time = defaultdict(lambda: 0)
        self.commit_hop = 0

        self.global_abort_num = 0
        self.local_abort_num = 0
        self.tx_abort_num = defaultdict(lambda: 0)
        self.global_abort_time = 0
        self.local_abort_time = 0
        self.tx_abort_time = defaultdict(lambda: 0)
        self.abort_hop = 0

        self.global_lock_start_time = 0
        self.global_lock_time = 0
        self.total_global_lock_time = 0

    def get_result(self, display=False):
        # commit: 8 (2 6)  6.20 (4.10 2.10)[s],   abort: 8 (4 4)  6.20 (4.07 2.13)[s]
        # commit
        commit_num = self.update_commit_num + self.read_commit_num
        commit_time = self.update_commit_time + self.read_commit_time
        commit_hop = utils.divide(self.commit_hop, self.update_commit_num)
        # abort
        abort_num = self.global_abort_num + self.local_abort_num
        abort_time = self.global_abort_time + self.local_abort_time
        abort_hop = utils.divide(self.abort_hop, self.global_abort_num)

        result = {
            "commit": [commit_num,  self.update_commit_num,  self.read_commit_num],
            "abort": [abort_num,  self.global_abort_num,  self.local_abort_num],
            "commit_time": [commit_time,  self.update_commit_time,  self.read_commit_time],
            "abort_time": [abort_time,  self.global_abort_time,  self.local_abort_time],
            "custom_commit": [self.update_commit_num*commit_hop,  self.update_commit_num,  commit_hop],
            "custom_abort": [self.global_abort_num*abort_hop,  self.global_abort_num,  abort_hop],
            "tx_commit": self.tx_commit_num,
            "tx_commit_time": self.tx_commit_time,
            "tx_abort": self.tx_abort_num,
            "tx_abort_time": self.tx_abort_time,
            "global_lock": [self.total_global_lock_time],
        }

        if display:
            rounded_result = utils.general_1obj_func(result, utils.round2)
            # commit
            commit_result = ""
            commit_result += "commit: {} ({} {})".format(*rounded_result["commit"]) + "  "
            commit_result += "{} ({} {})[s]".format(*rounded_result["commit_time"]) + ",   "
            commit_result += "{} = {} * {}".format(*rounded_result["custom_commit"])
            print(commit_result)
            # abort
            abort_result = ""
            abort_result += "abort: {} ({} {})".format(*rounded_result["abort"]) + "  "
            abort_result += "{} ({} {})[s]".format(*rounded_result["abort_time"]) + ",   "
            abort_result += "{} = {} * {}".format(*rounded_result["custom_abort"])
            print(abort_result)
            # each tx
            tx_type_set = set()
            tx_type_set |= set(rounded_result["tx_commit"].keys())
            tx_type_set |= set(rounded_result["tx_abort"].keys())
            for tx_type in sorted(tx_type_set):
                tx_result = ""
                tx_result += f"{tx_type}: "
                tx_result += f"{rounded_result["tx_commit"][tx_type]} {rounded_result["tx_abort"][tx_type]}  "
                tx_result += f"({rounded_result["tx_commit_time"][tx_type]} {rounded_result["tx_abort_time"][tx_type]})[s]"
                print(tx_result)
            # global lock
            print("global lock: {}[s]".format(*rounded_result["global_lock"]))
        return result

    def start_tx(self, tx_type=None):
        self.start_time = time.perf_counter()
        self.tx_type = tx_type

    def start_global_lock(self):
        self.global_lock_start_time = time.perf_counter()

    def finish_global_lock(self):
        self.global_lock_time = time.perf_counter() - self.global_lock_start_time

    def commit_tx(self, commit_type, hop=1):
        commit_time = time.perf_counter() - self.start_time
        if commit_type == 'update':
            self.update_commit_num += 1
            self.update_commit_time += commit_time
            self.commit_hop += hop
            self.total_global_lock_time += self.global_lock_time
        if commit_type == 'read':
            self.read_commit_num += 1
            self.read_commit_time += commit_time
        if self.tx_type:
            self.tx_commit_num[self.tx_type] += 1
            self.tx_commit_time[self.tx_type] += commit_time
            self.tx_type = None

    def abort_tx(self, abort_type, hop=1):
        abort_time = time.perf_counter() - self.start_time
        if abort_type == 'global':
            self.global_abort_num += 1
            self.global_abort_time += abort_time
            self.abort_hop += hop
        if abort_type == 'local':
            self.local_abort_num += 1
            self.local_abort_time += abort_time
        if self.tx_type:
            self.tx_abort_num[self.tx_type] += 1
            self.tx_abort_time[self.tx_type] += abort_time
            self.tx_type = None
