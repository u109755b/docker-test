import config
import rsabutils

class ValChange(object):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        # get params
        params = req.params
        
        about = params['about']
        
        if about == 'zipf' and not float(params['theta']) < -0.1:
            theta = float(params['theta'])
            rsabutils.ZIPF_GEN_MODE = True
            rsabutils.RECORDS_TX = 1
            record_num = len(config.candidate_record_id_list)
            rsabutils.zipf_gen = rsabutils.zipfGenerator(record_num-1, theta)
            print('set zipf {}'.format(theta))
                
        elif about == 'zipf' and float(params['theta']) < 0:
            rsabutils.ZIPF_GEN_MODE = False
            print('set zipf off')
            
            
        elif about == 'set_read_write_rate':
            rate = int(params['rate'])
            rsabutils.READ_WRITE_RATE = rate
            print('set rate {}'.format(rate))
        
        
        elif about == 'query_order':
            on_off = params['on_off']
            if on_off == 'off' or on_off == 'OFF':
                rsabutils.QUERY_ORDER = False
                print('set query_order off')
            elif on_off == 'on' or on_off == 'ON':
                rsabutils.QUERY_ORDER = True
                print('set query_order on')
            else:
                print('query_order parameter error')
            
        elif about == 'show_lock':
            lock_list = list(config.tx_dict)
            print('remaining lock: {}'.format(lock_list))
            
        msg = "finished"
        resp.text = msg
        return