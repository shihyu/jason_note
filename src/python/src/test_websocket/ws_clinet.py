import websocket
import time

# WebSocket服务器URL
websocket_url = "ws://localhost:8888/websocket"

while True:
    try:
        ws = websocket.WebSocket()
        ws.connect(websocket_url)
        time.sleep(1)

        while True:
            message = ws.recv()
            print(f"Received message from server: {message}")

    except Exception as e:
        print(f"An error occurred: {e}")

    # 在连接断开后等待一段时间再尝试重新连接
    time.sleep(5)
