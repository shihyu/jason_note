package main

import "fmt"

// {"op": "subscribe", "args": [{"channel": "books5", "instId": "BTC-USDT"}]}
var _wsProviderDef = map[string]string{
	"okcoinWsURL":      "wss://real.okcoin.com:8443/ws/v3",
	"okcoinWsWaitMsg":  ``,
	"okcoinWsSubMsg":   `{"op":"subscribe","args":["spot/depth:%s"]}`, // %s = BTC-USD
	"okcoinWsSubSplit": "",

	"bitfinexWsURL":      "wss://api-pub.bitfinex.com/ws/2",
	"bitfinexWsWaitMsg":  `"platform":{"status":1}`,
	"bitfinexWsSubMsg":   `{"event":"subscribe","channel":"book","symbol":"%s","len":"100"}`, // %s = BTCUSD
	"bitfinexWsSubSplit": "",

	"liquidWsURL":      "wss://tap.liquid.com/app/LiquidTapClient",
	"liquidWsWaitMsg":  `"event":"pusher:connection_established"`,
	"liquidWsSubMsg":   `{"event":"pusher:subscribe","data":{"channel":"price_ladders_cash_%s_sell"}}|{"event":"pusher:subscribe","data":{"channel":"price_ladders_cash_%s_buy"}}`, // %s = btcusd ; 一次要訂閱兩個 ... 用 | 分隔
	"liquidWsSubSplit": "|",

	"ftxWsURL":      "wss://ftx.com/ws/",
	"ftxWsWaitMsg":  ``,
	"ftxWsSubMsg":   `{"op":"subscribe","channel":"orderbook","market":"%s"}`, // %s = BTC-USD
	"ftxWsSubSplit": "",
}

func main() {
	wsSubMsg := _wsProviderDef[fmt.Sprintf("%sWsSubMsg", "okcoin")]
	fmt.Println(wsSubMsg)
	fmt.Printf("%T\n", wsSubMsg)
	s := fmt.Sprintf(wsSubMsg, "BTC-USDT")
	fmt.Println(s)
	//fmt.Println(wsSubMsg["args"])

}
