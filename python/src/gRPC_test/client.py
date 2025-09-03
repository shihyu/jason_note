# client.py 

import grpc
import time

import hello_pb2
import hello_pb2_grpc

# 連接到 localhost:50051
# channel = grpc.insecure_channel('localhost:50051')
channel = grpc.insecure_channel('202.182.118.167:50051')

# 創建一個 stub (gRPC client)
stub = hello_pb2_grpc.HelloStub(channel)
request = hello_pb2.HelloRequest(value="World")

while True:
    # 創建一個 HelloRequest 丟到 stub 去

    # 呼叫 Hello service，回傳 HelloResponse
    response = stub.Hello(request)

    print(response.value)
    time.sleep(0.1)
