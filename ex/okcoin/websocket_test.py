import asyncio
import websockets
import zlib
import json

omsg = {"op": "subscribe", "args": ["spot/depth:BTC-USDT"]}


def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


async def call_oapi(omsg):
    async with websockets.connect("wss://real.okcoin.com:8443/ws/v3") as websocket:
        await websocket.send(omsg)
        msg1 = await websocket.recv()
        msg2 = await websocket.recv()
        print(inflate(msg1).decode('utf-8'))
        print(inflate(msg2).decode('utf-8'))


def run(call_api, msg):
    asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))


run(call_oapi, omsg)
