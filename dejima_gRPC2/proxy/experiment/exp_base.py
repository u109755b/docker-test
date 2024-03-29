import json
from collections import defaultdict

import grpc
from grpcdata import data_pb2
from grpcdata import data_pb2_grpc

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.context import attach, detach, set_value

from dejima import config
from dejima import utils
from dejima import color

if config.trace_enabled:
    resource = Resource(attributes={"service.name": "dejima_client"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(endpoint="http://{}:4317".format(config.host_name), insecure=True)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )
    GrpcInstrumentorClient().instrument()

tracer = trace.get_tracer(__name__)


class ExperimentBase():
    # initialize
    def initialize(self):
        print("initialize")
        for i in range(self.peer_num):
            peer_name = f"Peer{i+1}"
            data = {"about": "initialize"}
            service_stub = data_pb2_grpc.ValChangeStub
            self.base_request(peer_name, data, service_stub, save_result=False, show_result=False)

    # base request
    def base_request(self, peer_name, data, service_stub, ctx=None, save_result=True, show_result=False):
        if ctx: token = attach(ctx)
        req = data_pb2.Request(json_str=json.dumps(data))
        peer_address = f"{peer_name}-proxy:8000"
        with grpc.insecure_channel(peer_address) as channel:
            stub = service_stub(channel)
            response = stub.on_get(req)
            if save_result:
                self.res_list.append(response.json_str)
            if show_result:
                params = json.loads(response.json_str)
                print(f'{peer_name}: {params["result"]}')
        if ctx: detach(token)


    # integrate result
    def integrate_result(self, res_list, peer_num, threads, show_result=True):
        thread_num = peer_num * threads

        all_data = {
            "basic_res": {
                "commit": [0, 0, 0],
                "abort": [0, 0, 0],
                "commit_time": [0, 0, 0],
                "abort_time": [0, 0, 0],
                "custom_commit": [0, 0, 0],
                "custom_abort": [0, 0, 0],
                "tx_commit": defaultdict(int),
                "tx_commit_time": defaultdict(int),
                "tx_abort": defaultdict(int),
                "tx_abort_time": defaultdict(int),
                "global_lock": [0],
            },
            "process_time": defaultdict(int),
            "lock_process": [0],
        }

        divider_data = {
            "basic_res": {
                "commit": [1, 1, 1],
                "abort": [1, 1, 1],
                "commit_time": [thread_num, thread_num, thread_num],
                "abort_time": [thread_num, thread_num, thread_num],
                "custom_commit": [1, 1, 1],
                "custom_abort": [1, 1, 1],
                "tx_commit": 1,
                "tx_commit_time": thread_num,
                "tx_abort": 1,
                "tx_abort_time": thread_num,
                "global_lock": [thread_num],
            },
            "process_time": thread_num,
            "lock_process": [thread_num],
        }

        basic_res = all_data["basic_res"]
        process_time = all_data["process_time"]
        global_lock = all_data["basic_res"]["global_lock"]
        lock_process = all_data["lock_process"]

        # 結果の合計
        for res in res_list:
            res = json.loads(res)
            if "result" in res:
                del res["result"]
            plus = lambda x, y: x + y
            utils.general_2obj_func(all_data, res, plus, save=True, assign_v2_value=True)

        # 結果の割り算
        utils.general_2obj_func(all_data, divider_data, utils.divide, save=True)

        # 全ピアにおける平均伝搬範囲を求める
        basic_res["custom_commit"][2] = utils.divide(basic_res["custom_commit"][0], basic_res["custom_commit"][1])
        basic_res["custom_abort"][2] = utils.divide(basic_res["custom_abort"][0], basic_res["custom_abort"][1])

        # 小数第2位に丸める
        utils.general_1obj_func(all_data, utils.round2, save=True)

        # その他の計算
        tx_time = basic_res["commit_time"][0] + basic_res["abort_time"][0]
        throughput = utils.divide(basic_res["commit"][0], tx_time)
        custom_throughput = utils.divide(basic_res["custom_commit"][0], tx_time)

        commit_time = basic_res["commit_time"][0]

        commit_per_peer = basic_res["commit"][0] / peer_num
        commit_time_per_commit = utils.divide(commit_time, commit_per_peer) * 1000
        global_lock_time_per_commit = utils.divide(global_lock[0], commit_per_peer) * 1000

        overall_result = [throughput, custom_throughput, commit_time, global_lock[0], commit_time_per_commit, global_lock_time_per_commit]
        utils.general_1obj_func(overall_result, utils.round2, save=True)

        # 結果表示
        if show_result:
            """ overall result """
            # print("throughput: {} {},  ({} {})[s],  ({} {})[ms]".format(*overall_result))
            result = f"{color.BLUE}throughput{color.RESET}:  "
            result += f"{color.PURPLE}{overall_result[0]}{color.RESET} {overall_result[1]},  "
            result += "({} {})[s],  ({} {})[ms]".format(*overall_result[2:])
            print(result)
            """ commit result """
            # commit_result = "commit:  {} ({} {})  {} ({} {})[s],   {} = {} * {}".format(*basic_res["commit"], *basic_res["commit_time"], *basic_res["custom_commit"])
            commit_result = f"{color.LIGHT_BLUE}commit{color.RESET}:  "
            commit_result += "{}{} ({} {}){}  ".format(color.GREEN, *basic_res["commit"], color.RESET)
            commit_result += "{}{} ({} {})[s]{},   ".format(color.GREEN, *basic_res["commit_time"], color.RESET)
            commit_result += "{} = {} * {}".format(*basic_res["custom_commit"])
            print(commit_result)
            """ abort result """
            # abort_result = "abort:  {} ({} {})  {} ({} {})[s],   {} = {} * {}".format(*basic_res["abort"], *basic_res["abort_time"], *basic_res["custom_abort"])
            abort_result = f"{color.LIGHT_BLUE}abort{color.RESET}:  "
            abort_result += "{}{} ({} {}){}  ".format(color.RED, *basic_res["abort"], color.RESET)
            abort_result += "{}{} ({} {})[s]{},   ".format(color.RED, *basic_res["abort_time"], color.RESET)
            abort_result += "{} = {} * {}".format(*basic_res["custom_abort"])
            print(abort_result)
            """ tx result """
            tx_type_set = set()
            tx_type_set |= set(basic_res["tx_commit"].keys())
            tx_type_set |= set(basic_res["tx_abort"].keys())
            for tx_type in sorted(tx_type_set):
                tx_result = ""
                tx_result += f"{color.BLUE}{tx_type}{color.RESET}:  "
                tx_result += color.set_green(f"{basic_res["tx_commit"][tx_type]}  ({basic_res["tx_commit_time"][tx_type]})[s]") + ",   "
                tx_result += color.set_red(f"{basic_res["tx_abort"][tx_type]}  ({basic_res["tx_abort_time"][tx_type]})[s]")
                print(tx_result)
            """ lock process """
            process_time_all = dict(sorted(process_time.items()))
            for group_name, each_group in process_time_all.items():
                each_group = dict(sorted(each_group.items()))
                total_time = utils.round2(sum(each_group.values()))
                print(f"{group_name}: {each_group} {total_time}[ms]")
            print(f"{utils.round2(lock_process[0])}[ms]")
