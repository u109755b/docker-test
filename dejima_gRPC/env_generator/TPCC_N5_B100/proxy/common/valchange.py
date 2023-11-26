import json
import config
import ycsbutils
import tpccutils
import random
import data_pb2
import data_pb2_grpc

# class ValChange(object):
class ValChange(data_pb2_grpc.ValChangeServicer):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        # get params
        # params = req.params
        params = json.loads(req.json_str)
        
        about = params['about']
        
        if about == 'zipf':
            if "theta" in params.keys():
                theta = float(params['theta'])
            else:
                theta = 0.5

            if "record_num" in params.keys():
                record_num = int(params['record_num'])
            else:
                record_num = 100000
                
            ycsbutils.zipf_gen = ycsbutils.zipfGenerator(record_num, theta)
            tpccutils.zipf_gen = tpccutils.zipfGenerator(record_num, theta)
            
            print('set zipf {}'.format(theta))
            # # Visualization of output
            # output_dict = {}
            # for _ in range(100000):
            #     index = next(rsabutils.zipf_gen)-1
            #     if config.peer_name.startswith('alliance'):
            #         n = rsabutils.RECORDS_PEER
            #         lower_bound = index//n * n
            #         upper_bound = lower_bound+n
            #         index = random.randint(lower_bound, upper_bound-1)
                
            #     id = config.candidate_record_id_list[index]
            #     if id not in output_dict:
            #         output_dict[id] = 0
            #     output_dict[id] += 1
            # output_dict = dict(sorted(output_dict.items(), key=lambda x: x[0]))
            # print(config.candidate_record_id_list)
            # print(output_dict)
            
        elif about == 'show_lock':
            lock_list = list(config.tx_dict)
            print('remaining lock: {}'.format(lock_list))

        elif about == 'prelock_valid':
            if "prelock_valid" in params.keys():
                if params['prelock_valid'] == True:
                    config.prelock_valid = True
                else:
                    config.prelock_valid = False
            print('set prelock_valid {}'.format(config.prelock_valid))

        elif about == 'plock_mode':
            if "plock_mode" in params.keys():
                if params['plock_mode'] == True:
                    config.plock_mode = True
                else:
                    config.plock_mode = False
            print('set plock_mode {}'.format(config.plock_mode))

        # msg = "finished"
        # resp.text = msg
        # return
        res_dic = {"result": "finished"}
        return data_pb2.Response(json_str=json.dumps(res_dic))