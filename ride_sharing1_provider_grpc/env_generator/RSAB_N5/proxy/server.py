import falcon
import sys
sys.dont_write_bytecode = True
app = falcon.App()

from concurrent.futures import ThreadPoolExecutor
import grpc
import data_pb2
import data_pb2_grpc
server = grpc.server(ThreadPoolExecutor(max_workers=100))

# FRS
from frs.propagation import FRSPropagation
# app.add_route("/frs/_propagate", FRSPropagation())
data_pb2_grpc.add_FRSPropagationServicer_to_server(FRSPropagation(), server)

from frs.termination import FRSTermination
# app.add_route("/frs/_terminate", FRSTermination())
data_pb2_grpc.add_FRSTerminationServicer_to_server(FRSTermination(), server)

from frs.lock import Lock
# app.add_route("/_lock", Lock())
data_pb2_grpc.add_LockServicer_to_server(Lock(), server)

from frs.unlock import Unlock
# app.add_route("/_unlock", Unlock())
data_pb2_grpc.add_UnlockServicer_to_server(Unlock(), server)

# 2PL
from two_pl.propagation import TPLPropagation
# app.add_route("/2pl/_propagate", TPLPropagation())
data_pb2_grpc.add_TPLPropagationServicer_to_server(TPLPropagation(), server)

from two_pl.termination import TPLTermination
# app.add_route("/2pl/_terminate", TPLTermination())
data_pb2_grpc.add_TPLTerminationServicer_to_server(TPLTermination(), server)

# # common
# from common.ycsb_load import YCSBLoad
# app.add_route("/load", YCSBLoad())

# from common.ycsb import YCSB
# app.add_route("/ycsb", YCSB())

# from common.tpcc_load_local import TPCCLoadLocal
# app.add_route("/localload_TPCC", TPCCLoadLocal())

# from common.tpcc_load_customer import TPCCLoadCustomer
# app.add_route("/customerload_TPCC", TPCCLoadCustomer())

# from common.tpcc import TPCC
# app.add_route("/tpcc", TPCC())

from common.rsab_load import RSABLoad
# app.add_route("/loadrsab", RSABLoad())
data_pb2_grpc.add_RSABLoadServicer_to_server(RSABLoad(), server)

from common.rsab import RSAB
# app.add_route("/rsab", RSAB())
data_pb2_grpc.add_RSABServicer_to_server(RSAB(), server)

# from common.execution import execution
# app.add_route("/execution", execution())

# from common.test import Test
# app.add_route("/_test", Test())

# from common.zipf import Zipf
# app.add_route("/zipf", Zipf())

# if __name__ == "__main__":
#     from wsgiref.simple_server import *
#     from socketserver import *
#     class ThreadingWsgiServer(ThreadingMixIn, WSGIServer):
#         pass

#     httpd = make_server('0.0.0.0', 8000, app, ThreadingWsgiServer)
#     print("serving on port 8000")
#     httpd.serve_forever()

import config
peer_name = config.dejima_config_dict["peer_address"][config.peer_name]
server.add_insecure_port("0.0.0.0:8000")
server.start()
server.wait_for_termination()