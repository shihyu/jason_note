# server.py
from concurrent import futures
import time

import grpc 
import hello_pb2
import hello_pb2_grpc

import hello

# 創建一個 HelloServicer，要繼承自 hello_pb2_grpc.HelloServicer
class HelloServicer(hello_pb2_grpc.HelloServicer):

# 由於我們 service 定義了 Hello 這個 rpc，所以要實作 Hello 這個 method
    def Hello(self, request, context):

# response 是個 HelloResponse 形態的 message
        response = hello_pb2.HelloResponse()
        response.value = hello.hello(request.value)
        return response


def serve():
# 創建一個 gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# 利用 add_HelloServicer_to_server 這個 method 把上面定義的 HelloServicer 加到 server 當中
    hello_pb2_grpc.add_HelloServicer_to_server(HelloServicer(), server)

# 讓 server 跑在 port 50051 中
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

