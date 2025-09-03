package main

import (
	"fmt"
	"github.com/gorilla/websocket"
	"log"
)

func subscribe(conn *websocket.Conn) {
	sub := `{"op": "subscribe", "args": [{"channel": "books5", "instId": "BTC-USDT"}]}`
	err := conn.WriteMessage(websocket.TextMessage, []byte(sub))
	if err != nil {
		panic(err)
	}
}

// https://github.com/binance-exchange/go-binance/blob/master/service_websocket.go
func main() {
	c, _, err := websocket.DefaultDialer.Dial("wss://ws.okx.com:8443/ws/v5/public", nil)
	if err != nil {
		log.Fatal("dial:", err)
	}
	subscribe(c)
	defer c.Close()

	// 启动一个协程，读取从服务端发送过来的数据
	go func() {
		for {
			messageType, messageByte, err := c.ReadMessage()
			if err != nil {
				fmt.Errorf("fail to read msg %s", err.Error())
			}

			//switch messageType {
			//case websocket.TextMessage: // no need uncompressed
			//	// do nothing
			//case websocket.BinaryMessage: // uncompressed (okcoin need)
			//}

			fmt.Println(string(messageByte), messageType)
		}
	}()

	// 阻塞主线程
	down := make(chan byte)
	for {
		<-down
	}
}
