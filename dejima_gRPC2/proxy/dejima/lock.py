import json
import time
from opentelemetry import trace
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc
from dejima import config
from dejima import errors
from dejima import measurement
from dejima import dejimautils
from dejima.transaction import Tx

tracer = trace.get_tracer(__name__)


class Lock(data_pb2_grpc.LockServicer):
    def __init__(self):
        pass

    @tracer.start_as_current_span("pre_lock")
    def on_post(self, req, resp):
        time.sleep(config.SLEEP_MS * 0.001)
        if config.prelock_invalid == True:
            res_dic = {"result": "Ack"}
            return data_pb2.Response(json_str=json.dumps(res_dic))

        params = json.loads(req.json_str)

        global_xid = params['xid']
        if config.include_getting_tx_time == True:
            measurement.time_measurement.start_timer("lock_process", global_xid)
        if config.getting_tx:
            tx = dejimautils.get_tx(global_xid, params["start_time"])
        if config.include_getting_tx_time == False:
            measurement.time_measurement.start_timer("lock_process", global_xid)


        # lock with lineages
        res_dic = {"result": "Nak"}
        try:
            dejimautils.lock_with_lineages(tx, params["lineages"], for_what="UPDATE")

        except errors.RecordsNotFound as e:
            return data_pb2.Response(json_str=json.dumps(res_dic))
        except errors.LockNotAvailable as e:
            # print(f"{os.path.basename(__file__)}: global lock failed")
            return data_pb2.Response(json_str=json.dumps(res_dic))


        measurement.time_measurement.stop_timer("lock_process", global_xid)

        res_dic = {"result": "Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
