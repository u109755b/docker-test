import json
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
import config
import measurement
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
            lock_list = list(config.tx_dict)
            print('remaining lock: {}'.format(lock_list))

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