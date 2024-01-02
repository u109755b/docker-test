import json
import config
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
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
            if "theta" in parameters.keys():
                theta = float(parameters['theta'])
            else:
                theta = 0.5

            if "record_num" in parameters.keys():
                record_num = int(parameters['record_num'])
            else:
                record_num = 100000

            ycsbutils.zipf_gen = ycsbutils.zipfGenerator(record_num, theta)
            tpccutils.zipf_gen = tpccutils.zipfGenerator(record_num, theta)

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
            config.time_measurement.init()
            print('initialized')

        res_dic = {"result": "finished"}
        return data_pb2.Response(json_str=json.dumps(res_dic))