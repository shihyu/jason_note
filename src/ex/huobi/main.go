package main

import (
	"bytes"
	"compress/gzip"
	"context"
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
	"io/ioutil"
	"log"
	"net/url"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
)

// https://www.anycodings.com/questions/go-negative-waitgroup-counter
// Structs

type Ping struct {
	Ping int64 `json:"ping"`
}

type Pong struct {
	Pong int64 `json:"pong"`
}

type SubParams struct {
	Sub string `json:"sub"`
	ID  string `json:"id"`
}

func InitSub(subType string, pair string, i int) []byte {
	var idInt string = "id" + strconv.Itoa(i)
	subStr := "market." + pair + "." + subType
	sub := &SubParams{
		Sub: subStr,
		ID:  idInt,
	}

	out, err := json.MarshalIndent(sub, "", " ")
	if err != nil {
		log.Println(err)
	}
	//log.Println(string(out))
	return out
}

// main func

func main() {
	var server string = "api.huobi.pro"
	pairs := []string{"btcusdt", "ethusdt", "ltcusdt"}
	comms := make(chan os.Signal, 1)
	signal.Notify(comms, os.Interrupt, syscall.SIGTERM)

	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	var wg sync.WaitGroup

	for x, pair := range pairs {
		wg.Add(1)
		go control(server, "ws", pair, ctx, &wg, x+1)
	}

	<-comms
	cancel()
	wg.Wait()
}

func control(server string, path string, pair string, ctx context.Context, wg *sync.WaitGroup, i int) {
	fmt.Printf("Started control for %s\n", server)
	url := url.URL{
		Scheme: "wss",
		Host:   server,
		Path:   path,
	}

	fmt.Println(url.String())

	conn, _, err := websocket.DefaultDialer.Dial(url.String(), nil)
	if err != nil {
		panic(err)
	}
	subscribe(conn, pair, i)
	defer conn.Close()

	var localwg sync.WaitGroup

	localwg.Add(1)
	go readHandler(ctx, conn, &localwg, server)

	<-ctx.Done()
	localwg.Wait()
	wg.Done()
	return
}

func readHandler(ctx context.Context, conn *websocket.Conn, wg *sync.WaitGroup, server string) {
	for {

		select {

		case <-ctx.Done():
			wg.Done()
			return
		default:
			_, p, err := conn.ReadMessage()
			if err != nil {
				wg.Done()
				fmt.Println(err)
				return
			}
			r, err := gzip.NewReader(bytes.NewReader(p))
			if err == nil {
				result, err := ioutil.ReadAll(r)
				if err != nil {
					fmt.Println(err)
				}
				d := string(result)
				fmt.Println(d)

				var ping Ping
				json.Unmarshal([]byte(d), &ping)
				if ping.Ping > 0 {
					str := Pong{Pong: ping.Ping}
					msg, err := json.Marshal(str)
					if err == nil {
						fmt.Println(string(msg))
						conn.WriteMessage(websocket.TextMessage, []byte(msg))
					}
				}
			}
		}
	}
}

func subscribe(conn *websocket.Conn, pair string, id int) {
	sub := string(InitSub("trade.detail", pair, id))
	fmt.Println(websocket.TextMessage, sub)

	err := conn.WriteMessage(websocket.TextMessage, []byte(sub))
	if err != nil {
		panic(err)
	}
}
