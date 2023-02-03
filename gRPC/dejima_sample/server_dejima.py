#!/usr/bin/env python3

# gRPCのサーバー実装ではThreadPoolを利用するので、そのためのモジュールをimportしておく
from concurrent.futures import ThreadPoolExecutor
import json

# 「grpc」パッケージと、grpc_tools.protocによって生成したパッケージをimportする
import grpc
import data_pb2
import data_pb2_grpc

import time
               
# サービス定義から生成されたクラスを継承して、定義したリモートプロシージャに対応するメソッドを実装する
class Lock(data_pb2_grpc.LockServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "Lock Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
        
class Unlock(data_pb2_grpc.UnlockServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "Unlock Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
        
class TPLPropagation(data_pb2_grpc.TPLPropagationServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "TPLPropagation Ack", "timestamps": [1, 2, 3]}
        return data_pb2.Response(json_str=json.dumps(res_dic))
        
class TPLTermination(data_pb2_grpc.TPLTerminationServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "TPLTermination Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))

class FRSPropagation(data_pb2_grpc.FRSPropagationServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "FRSPropagation Ack", "timestamps": [1, 2, 3]}
        return data_pb2.Response(json_str=json.dumps(res_dic))
        
class FRSTermination(data_pb2_grpc.FRSTerminationServicer):
    def on_post(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "FRSTermination Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))
        
class RSABLoad(data_pb2_grpc.RSABLoadServicer):
    def on_get(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "RSABLoad Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))

class RSAB(data_pb2_grpc.RSABServicer):
    def on_get(self, req, context):
        if req:
            params = json.loads(req.json_str)
            print(params)
        res_dic = {"result": "RSAB Ack"}
        return data_pb2.Response(json_str=json.dumps(res_dic))

def main():
    # Serverオブジェクトを作成する
    server = grpc.server(ThreadPoolExecutor(max_workers=2))

    # Serverオブジェクトに定義したServicerクラスを登録する
    data_pb2_grpc.add_LockServicer_to_server(Lock(), server)
    data_pb2_grpc.add_UnlockServicer_to_server(Unlock(), server)
    data_pb2_grpc.add_TPLPropagationServicer_to_server(TPLPropagation(), server)
    data_pb2_grpc.add_TPLTerminationServicer_to_server(TPLTermination(), server)
    data_pb2_grpc.add_FRSPropagationServicer_to_server(FRSPropagation(), server)
    data_pb2_grpc.add_FRSTerminationServicer_to_server(FRSTermination(), server)
    data_pb2_grpc.add_RSABLoadServicer_to_server(RSABLoad(), server)
    data_pb2_grpc.add_RSABServicer_to_server(RSAB(), server)

    # 1234番ポートで待ち受けするよう指定する
    server.add_insecure_port('localhost:1234')
    # server.add_insecure_port('0.0.0.0:1234')

    # 待ち受けを開始する
    server.start()
    print("start")

    # 待ち受け終了後の後処理を実行する
    server.wait_for_termination()
    
if __name__ == '__main__':
    main()