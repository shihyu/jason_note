package main

import (
	"bytes"
	"compress/flate"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"strconv"
	"time"

	"github.com/gorilla/websocket"
)

const FTX_OTC_KEY = "2r79G519vNcrMP5ebImxpCcB1AMWHz10F3wPkCSX"
const FYX_OTC_SECRET = "W5nGA04IFhotNwL3EltvELwxWjkW4ncNcwllYqk8"

var binanceId uint = 0

type okcoinWsPackageEvent struct {
	// sync.RWMutex
	Event   string `json:"event"`
	Channel string `json:"channel"`
}

type okcoinWsPackageRate struct {
	// sync.RWMutex
	Table  string `json:"table"`
	Action string `json:"action"`
	Data   []struct {
		InstrumentID string      `json:"instrument_id"`
		Asks         [][3]string `json:"asks"`
		Bids         [][3]string `json:"bids"`
	} `json:"data"`
	Timestamp string `json:"timestamp"`
	Checksum  int32  `json:"checksum"`
}

type binanceWsPackageRate struct {
	LastUpdateID int        `json:"lastUpdateId"`
	Bids         [][]string `json:"bids"`
	Asks         [][]string `json:"asks"`
}

type ftxWsPackageRate struct {
	Channel string `json:"channel"`
	Market  string `json:"market"`
	Type    string `json:"type"`
	Data    struct {
		Time     float64     `json:"time"`
		Checksum int64       `json:"checksum"`
		Bids     [][]float64 `json:"bids"`
		Asks     [][]float64 `json:"asks"`
		Action   string      `json:"action"`
	} `json:"data"`
}

type ftxOtcWsPackageRate struct {
	Type             string  `json:"type"`
	Channel          string  `json:"channel"`
	UserID           int     `json:"userId"`
	BaseCurrency     string  `json:"baseCurrency"`
	QuoteCurrency    string  `json:"quoteCurrency"`
	BaseCurrencySize float64 `json:"baseCurrencySize"`
}

var _wsProviderDef = map[string]string{
	"binanceWsURL":    "wss://stream.binance.com:9443/ws",
	"binanceWsSubMsg": `{"method": "SUBSCRIBE", "params": ["%s@depth20@100ms"], "id": ` + fmt.Sprintf("%d", binanceId) + `}`,

	"ftxOtcWsURL":    "wss://otc.ftx.com/ws",
	"ftxOtcWsSubMsg": `{"op": "subscribe", "channel": "quotes", "baseCurrency": "%s", "quoteCurrency": "USD", "baseCurrencySize": 100.0}`,

	"ftxWsURL":    "wss://ftx.com/ws/",
	"ftxWsSubMsg": `{"op":"subscribe","channel":"orderbook","market":"%s"}`, // %s = BTC/USD

	"bitfinexWsURL":    "wss://api-pub.bitfinex.com/ws/2",
	"bitfinexWsSubMsg": `{"event":"subscribe","channel":"book","symbol":"%s","len":"100"}`, // %s = BTCUSD

	"liquidWsURL":    "wss://tap.liquid.com/app/LiquidTapClient",
	"liquidWsSubMsg": `{"event":"pusher:subscribe","data":{"channel":"price_ladders_cash_%s_sell"}}`, // %s = btcusd ; 一次要訂閱兩個 ... 用 | 分隔

	"okcoinWsURL":    "wss://real.okcoin.com:8443/ws/v3",
	"okcoinWsSubMsg": `{"op":"subscribe","args":["spot/depth:%s"]}`,

	"okxWsURL":    "wss://ws.okx.com:8443/ws/v5/public",
	"okxWsSubMsg": `{"op": "subscribe", "args": [{"channel": "books5", "instId": "%s"}]}`,
}

func subscribe(conn *websocket.Conn, exchange string, pair string) {
	wsSubMsg := fmt.Sprintf(_wsProviderDef[fmt.Sprintf("%sWsSubMsg", exchange)], pair)
	err := conn.WriteMessage(websocket.TextMessage, []byte(wsSubMsg))
	if err != nil {
		panic(err)
	}
}

func updateData(exchange string, messageByte []byte) error {
	messageStr := string(messageByte)

	switch exchange {
	case "okcoin":
		var okWsEvent okcoinWsPackageEvent
		json.Unmarshal(messageByte, &okWsEvent)
		if &okWsEvent == nil {
			return fmt.Errorf("unknow package type okcoin 0.1 : %s", messageStr)
		}
		var okWsRate okcoinWsPackageRate
		json.Unmarshal(messageByte, &okWsRate)
		fmt.Println(exchange, okWsRate)
		return nil
	case "binance":
		var binanceWsRate binanceWsPackageRate
		err := json.Unmarshal(messageByte, &binanceWsRate)
		if err != nil {
			fmt.Println(exchange, "parse error: "+messageStr)
		} else {
			fmt.Println(exchange, binanceWsRate)
		}
		return nil
	case "ftx":
		var ftxWsRate ftxWsPackageRate
		err := json.Unmarshal(messageByte, &ftxWsRate)
		if err != nil {
			fmt.Println(exchange, "parse error: "+messageStr)
		} else {
			fmt.Println(exchange, ftxWsRate)
		}
		return nil
	case "ftxOtc":
		var ftxOtcWsRate ftxOtcWsPackageRate
		err := json.Unmarshal(messageByte, &ftxOtcWsRate)
		if err != nil {
			fmt.Println(exchange, "parse error: "+messageStr)
		} else {
			fmt.Println(exchange, ftxOtcWsRate)
		}
		return nil
	default:
		fmt.Println(exchange, messageStr)
		return nil
	}
}

func ws_init(exchange string, pair string) {
	c, _, err := websocket.DefaultDialer.Dial(_wsProviderDef[fmt.Sprintf("%sWsURL", exchange)], nil)
	if err != nil {
		log.Fatal("dial:", err)
	}

	if exchange == "ftxOtc" {
		ts := strconv.FormatInt(time.Now().UTC().Unix()*1000, 10)
		signature := sign(ts, []byte(FYX_OTC_SECRET))
		loginPayload := fmt.Sprintf(`{ "op": "login", "args": { "api_key": "%s", "sign": "%s", "timestamp": %s } }`, FTX_OTC_KEY, signature, ts)
		err := c.WriteMessage(websocket.TextMessage, []byte(loginPayload))
		if err != nil {
			panic(err)
		}
	}
	subscribe(c, exchange, pair)
	defer c.Close()

	for {
		messageType, messageByte, err := c.ReadMessage()
		if err != nil {
			fmt.Errorf("fail to read msg %s", err.Error())
		}

		switch messageType {
		case websocket.TextMessage: // no need uncompressed
		// do nothing
		case websocket.BinaryMessage: // uncompressed (okcoin need)
			messageByte, err = func() ([]byte, error) {
				reader := flate.NewReader(bytes.NewReader(messageByte))
				defer reader.Close()
				return ioutil.ReadAll(reader)
			}()
		}
		updateData(exchange, messageByte)
	}
}

func main() {
	go ws_init("okx", "BTC-USDT")
	go ws_init("okcoin", "BTC-USD")
	go ws_init("ftx", "BTC/USD")
	go ws_init("ftxOtc", "BTC")
	go ws_init("bitfinex", "BTCUSD")
	go ws_init("liquid", "btcusd")

	binanceId += 1
	go ws_init("binance", "btcusdt")

	// Blocking main thread
	down := make(chan byte)
	for {
		<-down
	}
}

func sign(signaturePayload string, secret []byte) string {
	mac := hmac.New(sha256.New, secret)
	mac.Write([]byte(signaturePayload))
	return hex.EncodeToString(mac.Sum(nil))
}
