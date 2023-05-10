import bitmex
import websocket
from bitmex_websocket import Instrument
from bitmex_websocket.constants import InstrumentChannels
import time
import datetime

urlBMX = 'http://www.bitmex.com/api/v1/position/leverage'

def process(data):
    for i in range(0, len(data)):
        print(data)
        '''
        if 'id' in data[i] and 'size' in data[i]:
            price = (8800000000 - data[i]['id']) / 100
            size = data[i]['size']
            side = data[i]['side']
            #if int(price * 2) < 40000:
                #priceData[int(price * 2)] = [price, size, side]
            print(datetime.datetime.now(),[price, size, side])
        '''
        '''
        #no size, I don't know why?
        else:
            price = (8800000000 - data[i]['id']) / 100
            #size = data[i]['size']
            side = data[i]['side']
            print([price,side])
        '''
while True:
    try :
        #time.sleep(10)
        clientBMX = bitmex.bitmex(test=False, api_key='PzhjOv7eIAKsjSLhmtz8Bx68', api_secret='Dy3ZWFOrG97ddefrx_9FVQMVGYow0DfpzhDXk7OcwsvRGZk3')

        #clientBMX = bitmex.bitmex(test=True, api_key='Lqv0J_ddAK0zog_yv0goLMG8', api_secret='eLcXefzEcDQNyk9Hooui92ZLNhYIXBKsV9xVLqv8TGeNoAr2')

        print('Initialize........')
        websocket.enableTrace(True)
        channels = [
            InstrumentChannels.orderBook10,
            InstrumentChannels.quoteBin1m
        ]
        Bitmex = Instrument(symbol='XBTUSD',channels=channels)
        Bitmex.on('action', lambda msg: process(msg['data']))
        Bitmex.run_forever()
    except:
        time.sleep(10)

'''
clientBMX.Order.Order_new(symbol='XBTUSD', orderQty = Amount, price=priceSell-12.5).result()
clientBMX.Order.Order_cancel(orderID=orders[k]['orderID']).result()
orders = clientBMX.Order.Order_getOrders(filter=json.dumps({"open": True,"symbol":"XBTUSD"})).result()[0]
'''