# Python WebSocket長連接心跳與短連接

**安裝**

```
pip install websocket-client
```

先來看一下，長連接調用方式：

```python
ws = websocket.WebSocketApp(
    "ws://echo.websocket.org/",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.on_open = on_open
ws.run_forever()
```

 **長連接，參數介紹：**

（1）url: websocket的地址。

（2）header: 客戶發送websocket握手請求的請求頭，{'head1:value1','head2:value2'}。

（3）on_open：在建立Websocket握手時調用的可調用對象，這個方法只有一個參數，就是該類本身。

（4）on_message：這個對像在接收到服務器返回的消息時調用。有兩個參數，一個是該類本身，一個是我們從服務器獲取的字符串（utf-8格式）。

（5）on_error：這個對像在遇到錯誤時調用，有兩個參數，第一個是該類本身，第二個是異常對象。

（6）on_close：在遇到連接關閉的情況時調用，參數只有一個，就是該類本身。

（7）on_cont_message：這個對像在接收到連續幀數據時被調用，有三個參數，分別是：類本身，從服務器接受的字符串（utf-8），連續標志。

（8）on_data：當從服務器接收到消息時被調用，有四個參數，分別是：該類本身，接收到的字符串（utf-8），數據類型，連續標志。

（9）keep_running：一個二進制的標志位，如果為True，這個app的主循環將持續運行，默認值為True。

（10）get_mask_key：用於產生一個掩碼。

（11）subprotocols：一組可用的子協議，默認為空。

**長連接關鍵方法：**ws.run_forever(ping_interval=60,ping_timeout=5)

如果不斷開關閉websocket連接，會一直阻塞下去。另外這個函數帶兩個參數，如果傳的話，啟動心跳包發送。

ping_interval:自動發送“ping”命令，每個指定的時間(秒),如果設置為0，則不會自動發送。

ping_timeout:如果沒有收到pong消息，則為超時(秒)。

```python
ws.run_forever(ping_interval=60, ping_timeout=5)
# ping_interval心跳發送間隔時間
# ping_timeout 設置，發送ping到收到pong的超時時間
```

**我們看源代碼，會發現這樣一斷代碼：**

ping的超時時間，要大於ping間隔時間

```python
if not ping_timeout or ping_timeout <= 0:
    ping_timeout = None
if ping_timeout and ping_interval and ping_interval <= ping_timeout:
    raise WebSocketException("Ensure ping_interval > ping_timeout")
```

**長連接：**

**示例1：**

```python
import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        ws.send("hello1")
        time.sleep(1)
        ws.close()

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://echo.websocket.org/",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    ws.run_forever(ping_interval=60, ping_timeout=5)
```

**示例2：**

```python
import websocket
from threading import Thread
import time
import sys


class MyApp(websocket.WebSocketApp):
    def on_message(self, message):
        print(message)

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def on_open(self):
        def run(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesn't exit and socket
                # isn't closed
                self.send("Hello %d" % i)
                time.sleep(1)

            time.sleep(1)
            self.close()
            print("Thread terminating...")

        Thread(target=run).start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://echo.websocket.org/"
    else:
        host = sys.argv[1]
    ws = MyApp(host)
    ws.run_forever()
```

**短連接：**

```python
from websocket import create_connection
ws = create_connection("ws://echo.websocket.org/")
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
```



出處

https://www.bbsmax.com/A/pRdBKapazn/



---

## python websocket 斷線自動重連

先定義連接函數

```python
def connection_tmp(ws):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8000/ws",
                              on_message = on_message,
                            #   on_data=on_data_test,
                              on_error = on_error,
                              on_close = on_close)
    
    ws.on_open = on_open
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()  
    except:
        ws.close() 
```

再定義錯誤函數

```python
def on_error(ws, error):

    global reconnect_count
    print(type(error))
    print(error)
    if type(error)==ConnectionRefusedError or type(error)==websocket._exceptions.WebSocketConnectionClosedException:
        print("正在嘗試第%d次重連"%reconnect_count)
        reconnect_count+=1
        if reconnect_count<100:
            connection_tmp(ws)
    else:
        print("其他error!")
```

設置屬性全部global即可

```python
global reconnect_count
global ws
ws=None
reconnect_count=0
<class 'websocket._exceptions.WebSocketConnectionClosedException'>
Connection is already closed.
正在嘗試第4次重連
<class 'KeyboardInterrupt'>

其他error!
### closed ###!
### closed ###!
### closed ###!
### closed ###!
### closed ###!
### closed ###!
```



出處

https://www.cxybb.com/article/u013673826/105605631
