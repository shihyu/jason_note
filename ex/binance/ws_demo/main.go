package main

import (
	"fmt"
	"log"

	"github.com/gorilla/websocket"
)

// https://github.com/binance-exchange/go-binance/blob/master/service_websocket.go
func main() {
	c, _, err := websocket.DefaultDialer.Dial("wss://stream.binance.com:9443/ws/btsusdt@depth20@100ms", nil)
	if err != nil {
		log.Fatal("dial:", err)
	}
	defer c.Close()

	// 启动一个协程，读取从服务端发送过来的数据
	go func() {
		for {
			_, message, _ := c.ReadMessage()
			fmt.Println(string(message))
		}
	}()

	// 阻塞主线程
	down := make(chan byte)
	for {
		<-down
	}
}
