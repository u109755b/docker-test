import json
from collections import Counter
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import adrutils
from dejima import measurement
from benchmark import benchutils
from benchmark.ycsb import ycsbutils
from benchmark.tpcc import tpccutils

class ValChange(data_pb2_grpc.ValChangeServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        params = json.loads(req.json_str)

        about = params['about']

        if about == 'zipf':
            parameters = params['parameter']
            record_num = int(parameters['record_num'])
            theta = float(parameters['theta'])

            tpccutils.zipf_gen = benchutils.ZipfGenerator(record_num, theta)
            ycsbutils.zipf_gen = benchutils.ZipfGenerator(record_num, theta)

            print('set zipf {}'.format(theta))


        elif about == 'show_lock':
            # remaining lock
            lock_list = list(config.tx_dict)
            remaining_lock = f"remaining lock: {lock_list}"

            # # r_directions
            # r_direction_counter = Counter(frozenset(r_directions) for r_directions in adrutils.r_direction.values())
            # if frozenset() in r_direction_counter: del r_direction_counter[frozenset()]
            # r_direction_counter = ', '.join(f'{set(key)}: {count}' for key, count in r_direction_counter.items())
            # r_directions = f"r_directions: {r_direction_counter}"

            # # request count
            # request_counter = Counter(len(request_count) for request_count in adrutils.request_count.values())
            # request_counter = sorted(dict(request_counter).items())
            # request_count = f"request_count: {request_counter}"

            # r non-r records
            entry_count = len(adrutils.is_r_peer)
            r_count = sum(is_r == True for is_r in adrutils.is_r_peer.values())
            edge_r_count = sum(is_edge == True for is_edge in adrutils.is_edge_r_peer.values())
            non_r_count = len(adrutils.is_r_peer) - r_count
            non_edge_r_count = r_count - edge_r_count
            r_nonr_records = f"r_non-r_record: ({entry_count} {non_edge_r_count} {edge_r_count} {non_r_count})"

            # ec count
            log_count = len(adrutils.ec_manager.log)
            expansion_count = sum(log == "expansion" for log in adrutils.ec_manager.log)
            contraction_count = sum(log == "contraction" for log in adrutils.ec_manager.log)
            entropy = round(adrutils.ec_manager.get_entropy(), 2)
            read_log_look_range = adrutils.ec_manager.get_log_look_range("read")
            update_log_look_range = adrutils.ec_manager.get_log_look_range("update")
            ec_count = f"ec_count: ({log_count} {expansion_count} {contraction_count} {entropy} {read_log_look_range} {update_log_look_range})"

            # prop time
            lock_time, base_update_time, prop_view_time, total_prop_time = adrutils.get_update_prop_time()
            update_prop_time = f"{round(total_prop_time*1000, 2)} ({round(lock_time*1000, 2)}, {round(base_update_time*1000, 2)}, {round(prop_view_time*1000, 2)})"
            read_prop_time = round(adrutils.get_read_prop_time()*1000, 2)
            prop_time = f"{update_prop_time} {read_prop_time} [ms]"

            # # tx type count
            # tx_type_count = ' '.join([f'{key} {config.tx_type_count[key]}' for key in sorted(config.tx_type_count)])

            # output
            output = ",  ".join([r_nonr_records, ec_count, prop_time])
            print(output)


        elif about == 'prelock_request_invalid':
            config.prelock_request_invalid = params['parameter']
            print('set prelock_request_invalid {}'.format(config.prelock_request_invalid))

        elif about == 'prelock_invalid':
            config.prelock_invalid = params['parameter']
            print('set prelock_invalid {}'.format(config.prelock_invalid))

        elif about == 'hop_mode':
            config.hop_mode = params['parameter']
            print('set hop_mode {}'.format(config.hop_mode))

        elif about == 'include_getting_tx_time':
            config.include_getting_tx_time = params['parameter']
            print('set include_getting_tx_time {}'.format(config.include_getting_tx_time))

        elif about == 'getting_tx':
            config.getting_tx = params['parameter']
            print('set getting_tx {}'.format(config.getting_tx))

        elif about == 'initialize':
            measurement.time_measurement.init()
            print('initialized')

        res_dic = {"result": "finished"}
        return data_pb2.Response(json_str=json.dumps(res_dic))