from ast import literal_eval
import websocket
import sys
import hashlib
import zlib


def on_open(self):
    self.send('{"op": "subscribe", "args": ["spot/depth:BTC-USD"]}')


def on_message(self, evt):
    data = inflate(evt).decode('utf-8')  # data decompress
    data = literal_eval(data)
    print(data['data'])


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # see above
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def on_error(self, evt):
    print(evt)


def on_close(self, evt):
    print("DISCONNECT")


if __name__ == "__main__":
    host = "wss://real.okcoin.com:8443/ws/v3"
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        host, on_message=on_message, on_error=on_error, on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
