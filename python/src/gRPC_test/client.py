# client.py 

import grpc

import hello_pb2
import hello_pb2_grpc

# 連接到 localhost:50051
channel = grpc.insecure_channel('localhost:50051')

# 創建一個 stub (gRPC client)
stub = hello_pb2_grpc.HelloStub(channel)

# 創建一個 HelloRequest 丟到 stub 去
request = hello_pb2.HelloRequest(value="World")

# 呼叫 Hello service，回傳 HelloResponse
response = stub.Hello(request)

print(response.value)
