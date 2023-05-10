package main

import (
	"bytes"
	"compress/flate"
	"fmt"
	"github.com/gorilla/websocket"
	"io/ioutil"
	"log"
)

func subscribe(conn *websocket.Conn) {
	sub := `{"op": "subscribe", "args": ["spot/depth:BTC-USDT"]}`
	// sub := `{"op": "subscribe", "args": ["spot/depth:ETH-USDT"]}`
	err := conn.WriteMessage(websocket.TextMessage, []byte(sub))
	if err != nil {
		panic(err)
	}
}

// https://github.com/binance-exchange/go-binance/blob/master/service_websocket.go
func main() {
	c, _, err := websocket.DefaultDialer.Dial("wss://real.okcoin.com:8443/ws/v3", nil)
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
			fmt.Println(string(messageByte), messageType)
		}
	}()

	// 阻塞主线程
	down := make(chan byte)
	for {
		<-down
	}
}
