import falcon
import sys
sys.dont_write_bytecode = True

from concurrent.futures import ThreadPoolExecutor
import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.falcon import FalconInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

from dejima import config

if config.trace_enabled:
    resource = Resource(attributes={"service.name": "dejima_server"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(endpoint="http://{}:4317".format(config.host_name), insecure=True)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )
    FalconInstrumentor().instrument()
    GrpcInstrumentorServer().instrument()

app = falcon.App()
server = grpc.server(ThreadPoolExecutor(max_workers=2000))


# Dejima
from dejima.lock import Lock
data_pb2_grpc.add_LockServicer_to_server(Lock(), server)

from dejima.unlock import Unlock
data_pb2_grpc.add_UnlockServicer_to_server(Unlock(), server)

from dejima.propagation import Propagation
data_pb2_grpc.add_PropagationServicer_to_server(Propagation(), server)

from dejima.termination import Termination
data_pb2_grpc.add_TerminationServicer_to_server(Termination(), server)

from dejima.valchange import ValChange
data_pb2_grpc.add_ValChangeServicer_to_server(ValChange(), server)

# Benchmark
from benchmark.load_data import LoadData
data_pb2_grpc.add_LoadDataServicer_to_server(LoadData(), server)

from benchmark.benchmark import Benchmark
data_pb2_grpc.add_BenchmarkServicer_to_server(Benchmark(), server)


if __name__ == "__main__":    
    peer_name = config.dejima_config_dict["peer_address"][config.peer_name]
    server.add_insecure_port("0.0.0.0:8000")
    server.start()
    print("serving on port 8000")
    server.wait_for_termination()
