

## WebSocket



```go
package main

import (
	"log"
    "fmt"

	"github.com/gorilla/websocket"
)

// https://github.com/binance-exchange/go-binance/blob/master/service_websocket.go
func main() {
	c, _, err := websocket.DefaultDialer.Dial("wss://stream.binance.com:9443/ws/btsusdt@depth20@100ms", nil)
	if err != nil {
		log.Fatal("dial:", err)
	}
	defer c.Close()

	// 啟動一個協程，讀取從服務端發送過來的數據
	go func() {
		for {
			_, message, _ := c.ReadMessage()
			fmt.Println(string(message))
		}
	}()

	// 阻塞主線程
	down := make(chan byte)
	for {
		<-down
	}
}
```



```go
func main() {

    // 定義客戶端的地址
    u := url.URL{Scheme: "ws", Host: "locaalhost:999", Path: "/connect"}

    // 與客戶端建立連接
    c, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
    if err != nil {
        log.Fatal("dial:", err)
    }
    defer c.Close()

    // 啟動一個協程，讀取從服務端發送過來的數據
    go func() {
        for {
            _, message, _ := c.ReadMessage()
            fmt.Println(string(message))
        }
    }()


    // 阻塞主線程
    down := make(chan byte)
    for {
        <-down
    }
}
```

```go
package main

import (
    "flag"
    "fmt"
    "github.com/gorilla/websocket"
    "log"
    "net/url"
)

var addr = flag.String("addr", "localhost:9999", "proxy server addr")

func main() {

    u := url.URL{Scheme: "ws", Host: *addr, Path: "/connect"}

    c, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
    if err != nil {
        log.Fatal("dial:", err)
    }
    defer c.Close()

    down := make(chan byte)
    go func() {
        for {
            _, message, _ := c.ReadMessage()
            fmt.Println("服務端發送:" + string(message))
        }
    }()

    go func() {
        for {
            var input string
            fmt.Scanln(&input)
            c.WriteMessage(websocket.TextMessage, []byte(input))
        }
    }()

    for {
        <-down
    }
}
```

