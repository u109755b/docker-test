import falcon
import sys
sys.dont_write_bytecode = True

app = falcon.App()

# FRS
from frs.propagation import FRSPropagation
app.add_route("/frs/_propagate", FRSPropagation())

from frs.termination import FRSTermination
app.add_route("/frs/_terminate", FRSTermination())

from frs.lock import Lock
app.add_route("/_lock", Lock())

from frs.unlock import Unlock
app.add_route("/_unlock", Unlock())

# 2PL
from two_pl.propagation import TPLPropagation
app.add_route("/2pl/_propagate", TPLPropagation())

from two_pl.termination import TPLTermination
app.add_route("/2pl/_terminate", TPLTermination())

# common
from common.ycsb import YCSB
app.add_route("/ycsb", YCSB())

from common.test import Test
app.add_route("/_test", Test())

from common.zipf import Zipf
app.add_route("/zipf", Zipf())

from common.ycsb_load import YCSBLoad
app.add_route("/load", YCSBLoad())

from common.tpcc_load_local import TPCCLoadLocal
app.add_route("/localload_TPCC", TPCCLoadLocal())

from common.tpcc_load_customer import TPCCLoadCustomer
app.add_route("/customerload_TPCC", TPCCLoadCustomer())

from common.tpcc import TPCC
app.add_route("/tpcc", TPCC())

if __name__ == "__main__":
    from wsgiref.simple_server import *
    from socketserver import *
    class ThreadingWsgiServer(ThreadingMixIn, WSGIServer):
        pass

    httpd = make_server('0.0.0.0', 8000, app, ThreadingWsgiServer)
    print("serving on port 8000")
    httpd.serve_forever()
