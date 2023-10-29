import config
import ycsbutils
import random

class ValChange(object):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        # get params
        params = req.params
        
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
            
        msg = "finished"
        resp.text = msg
        return