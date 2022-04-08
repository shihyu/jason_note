# 教你用Python搭建gRPC服務



gRPC是一個高效能、通用的開源RPC框架，其由Google主要面向移動應用開發並基於HTTP/2協議標準而設計，基於ProtoBuf序列化協議開發，且支援眾多開發語言。一個gRPC服務的大體結構圖為：




![技術實踐：教你用Python搭建gRPC服務](https://i.iter01.com/images/f590cd3ff1eb5c75b4a9fc6cd554fa80c007ba02ead30acb497a56a808ee72ba.png)

圖一表明，grpc的服務是跨語言的，但需要遵循相同的協議（proto）。相比於REST服務，gPRC 的一個很明顯的優勢是它使用了二進位制編碼，所以它比 JSON/HTTP 更快，且有清晰的介面規範以及支援流式傳輸，但它的實現相比rest服務要稍微要複雜一些，下面簡單介紹搭建gRPC服務的步驟。

## 1.安裝python需要的庫

```
pip install grpcio
pip install grpcio-tools  
pip install protobuf
```

## 2.定義gRPC的介面

建立 gRPC 服務的第一步是在.proto 檔案中定義好介面，proto是一個協議檔案，客戶端和伺服器的通訊介面正是通過proto檔案協定的，可以根據不同語言生成對應語言的程式碼檔案。這個協議檔案主要就是定義好服務（service）介面，以及請求引數和相應結果的資料結構，具體的proto語法參見如下連結（https://www.jianshu.com/p/da7ed5914088），關於二維陣列、字典等python中常用的資料型別，proto語法的表達見連結（https://blog.csdn.net/xiaoxiaojie521/article/details/106938519），下面是一個簡單的例子。

```
syntax = "proto3";

option cc_generic_services = true;

//定義服務介面
service GrpcService {
    rpc hello (HelloRequest) returns (HelloResponse) {}  //一個服務中可以定義多個介面，也就是多個函式功能
}

//請求的引數
message HelloRequest {
    string data = 1;   //數字1,2是引數的位置順序，並不是對引數賦值
    Skill skill = 2;  //支援自定義的資料格式，非常靈活
};

//返回的物件
message HelloResponse {
    string result = 1;
    map<string, int32> map_result = 2; //支援map資料格式，類似dict
};

message Skill {
    string name = 1;
};
```

## 3.使用 protoc 和相應的外掛編譯生成對應語言的程式碼

```
python -m grpc_tools.protoc -I ./ --python_out=./ --grpc_python_out=. ./hello.proto
```

利用編譯工具把proto檔案轉化成py檔案，直接在當前檔案目錄下執行上述程式碼即可。

1. -I 指定proto所在目錄
2. -m 指定通過protoc生成py檔案
3. --python_out指定生成py檔案的輸出路徑
4. hello.proto 輸入的proto檔案

執行上述命令後，生成hello_pb2.py 和hello_pb2_grpc.py這兩個檔案。

## 4.編寫grpc的服務端程式碼

```python
#! /usr/bin/env python
# coding=utf8

import time
from concurrent import futures

import grpc

from gRPC_example import hello_pb2_grpc, hello_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class TestService(hello_pb2_grpc.GrpcServiceServicer):
    '''
    繼承GrpcServiceServicer,實現hello方法
    '''
    def __init__(self):
        pass

    def hello(self, request, context):
        '''
        具體實現hello的方法，並按照pb的返回物件構造HelloResponse返回
        :param request:
        :param context:
        :return:
        '''
        result = request.data + request.skill.name + " this is gprc test service"
        list_result = {"12": 1232}
        return hello_pb2.HelloResponse(result=str(result),
                                       map_result=list_result)

def run():
    '''
    模擬服務啟動
    :return:
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_GrpcServiceServicer_to_server(TestService(),server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("start service...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run()
```

在服務端側，需要實現hello的方法來滿足proto檔案中GrpcService的介面需求，hello方法的傳入引數，是在proto檔案中定義的HelloRequest，context是保留欄位，不用管，返回引數則是在proto中定義的HelloResponse，服務啟動的程式碼是標準的，可以根據需求修改提供服務的ip地址以及埠號。

## 5.編寫gRPC客戶端的程式碼

```python
#! /usr/bin/env python
# coding=utf8

import grpc

from gRPC_example import #! /usr/bin/env python
# coding=utf8

import grpc

from gRPC_example import hello_pb2_grpc, hello_pb2


def run():
    '''
    模擬請求服務方法資訊
    :return:
    '''
    conn=grpc.insecure_channel('localhost:50052')
    client = hello_pb2_grpc.GrpcServiceStub(channel=conn)
    skill = hello_pb2.Skill(name="engineer")
    request = hello_pb2.HelloRequest(data="xiao gang", skill=skill)
    respnse = client.hello(request)
    print("received:",respnse.result)


if __name__ == '__main__':
    run()


def run():
    '''
    模擬請求服務方法資訊
    :return:
    '''
    conn=grpc.insecure_channel('localhost:50052')
    client = hello_pb2_grpc.GrpcServiceStub(channel=conn)
    skill = hello_pb2.Skill(name="engineer")
    request = hello_pb2.HelloRequest(data="xiao gang", skill=skill)
    response = client.hello(request)
    print("received:",response.result)


if __name__ == '__main__':
    run()
```

客戶端側程式碼的實現比較簡單，首先定義好訪問ip和埠號，然後定義好HelloRequest資料結構，遠端呼叫hello即可。需要強調的是，客戶端和服務端一定要import相同proto檔案編譯生成的hello_pb2_grpc, hello_pb2模組，即使服務端和客戶端使用的語言不一樣，這也是grpc介面規範一致的體現。

## 6.呼叫測試

先啟動執行服務端的程式碼，再啟動執行客戶端的程式碼即可。

## 7.gRPC的使用總結

1. 定義好介面文件
2. 工具生成服務端/客戶端程式碼
3. 服務端補充業務程式碼
4. 客戶端建立 gRPC 連線後，使用自動生成的程式碼呼叫函式
5. 編譯、執行