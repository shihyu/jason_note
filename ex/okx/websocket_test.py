import asyncio
import websockets
import json

# https://solveforum.com/forums/threads/solved-how-to-run-multiple-websocket-api-calls-concurrently.812919/

# omsg = {"op": "subscribe", "args": [{"channel": "instruments", "instType": "FUTURES"}]}
# omsg = {"op": "subscribe", "args": [{"channel": "books", "instId": "BTC-USDT"}]}
omsg = {"op": "subscribe", "args": [{"channel": "books5", "instId": "BTC-USDT"}]}
dmsg = {
    "jsonrpc": "2.0",
    "method": "public/get_index_price",
    "id": 1,
    "params": {"index_name": "btc_usd"},
}


async def call_oapi(omsg):
    async with websockets.connect(
        # "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
        # "wss://ws.okx.com:8443/ws/v5/public"
        "wss://ws.okx.com:8443/ws/v5/public"
    ) as websocket:
        print(omsg)
        input()
        await websocket.send(omsg)
        response1 = await websocket.recv()
        response2 = await websocket.recv()
        print(response1)
        print(response2)


async def call_dapi(dmsg):
    async with websockets.connect("wss://test.deribit.com/ws/api/v2") as websocket:
        await websocket.send(dmsg)
        response = await websocket.recv()
        print(response)


def run(call_api, msg):
    asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))


# run(call_dapi, dmsg)
run(call_oapi, omsg)
