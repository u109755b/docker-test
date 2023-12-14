import falcon
import sys
sys.dont_write_bytecode = True

import falcon
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.falcon import FalconInstrumentor

resource = Resource(attributes={"service.name": "dejima_server"})
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint="http://host.docker.internal:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

app = falcon.App()
FalconInstrumentor().instrument()

from concurrent.futures import ThreadPoolExecutor
import grpc
import data_pb2
import data_pb2_grpc
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

GrpcInstrumentorServer().instrument()
server = grpc.server(ThreadPoolExecutor(max_workers=2000))

# FRS
from frs.propagation import FRSPropagation
data_pb2_grpc.add_FRSPropagationServicer_to_server(FRSPropagation(), server)

from frs.termination import FRSTermination
data_pb2_grpc.add_FRSTerminationServicer_to_server(FRSTermination(), server)

from frs.lock import Lock
data_pb2_grpc.add_LockServicer_to_server(Lock(), server)

from frs.unlock import Unlock
data_pb2_grpc.add_UnlockServicer_to_server(Unlock(), server)

# 2PL
from two_pl.propagation import TPLPropagation
data_pb2_grpc.add_TPLPropagationServicer_to_server(TPLPropagation(), server)

from two_pl.termination import TPLTermination
data_pb2_grpc.add_TPLTerminationServicer_to_server(TPLTermination(), server)

# common
from common.ycsb_load import YCSBLoad
data_pb2_grpc.add_YCSBLoadServicer_to_server(YCSBLoad(), server)

from common.ycsb import YCSB
data_pb2_grpc.add_YCSBServicer_to_server(YCSB(), server)

from common.tpcc_load_local import TPCCLoadLocal
data_pb2_grpc.add_TPCCLoadLocalServicer_to_server(TPCCLoadLocal(), server)

from common.tpcc_load_customer import TPCCLoadCustomer
data_pb2_grpc.add_TPCCLoadCustomerServicer_to_server(TPCCLoadCustomer(), server)

from common.tpcc import TPCC
data_pb2_grpc.add_TPCCServicer_to_server(TPCC(), server)

from common.valchange import ValChange
data_pb2_grpc.add_ValChangeServicer_to_server(ValChange(), server)

if __name__ == "__main__":    
    import config
    peer_name = config.dejima_config_dict["peer_address"][config.peer_name]
    server.add_insecure_port("0.0.0.0:8000")
    server.start()
    print("serving on port 8000")
    server.wait_for_termination()
