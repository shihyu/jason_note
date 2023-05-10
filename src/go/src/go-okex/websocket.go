package okex

import (
	"context"
	"fmt"
	"log"
	"time"

	//"github.com/gorilla/websocket"
	. "github.com/tbtc-bot/go-okex/common"
	. "github.com/tbtc-bot/go-okex/impl"
	. "github.com/tbtc-bot/go-okex/interface"
	"nhooyr.io/websocket"
)

// WsHandler handle raw websocket message
type WsHandler func(message []byte)

// ErrHandler handles errors
type ErrHandler func(err error)

// WsConfig webservice configuration
type WsConfig struct {
	Endpoint   string
	WsOp       WSReqData
	ApiKey     *string
	SecretKey  *string
	PassPhrase *string
}

func newWsConfig(endpoint string, wsop WSReqData, apiKey string, secretKey string, passphrase string) *WsConfig {
	return &WsConfig{
		Endpoint:   endpoint,
		WsOp:       wsop,
		ApiKey:     &apiKey,
		SecretKey:  &secretKey,
		PassPhrase: &passphrase,
	}
}

// websocket manager for public endpoint
var wsServe = func(cfg *WsConfig, handler WsHandler, errHandler ErrHandler) (doneC, stopC chan struct{}, err error) {
	ctx, cancel := context.WithCancel(context.Background())
	c, _, err := websocket.Dial(ctx, cfg.Endpoint, nil)
	if err != nil {
		log.Fatal("Error to dial websocket: ", err)
		cancel()
		return nil, nil, err
	}
	c.SetReadLimit(655350)

	// send login for private channel
	if *cfg.ApiKey != "" {
		//timestamp := IsoTime()
		timestamp := time.Now().Unix()
		sign, err := Hmac256(fmt.Sprint(timestamp), "GET", "/users/self/verify", nil, *cfg.SecretKey)
		if err != nil {
			log.Fatal("Error authentication websocket (generating key): ", err)
			cancel()
		}
		arg := map[string]string{
			"apiKey":     *cfg.ApiKey,
			"passphrase": *cfg.PassPhrase,
			"timestamp":  fmt.Sprint(timestamp),
			"sign":       sign,
		}
		var args []map[string]string
		args = append(args, arg)
		WsOp := ReqData{Op: "login",
			Args: args,
		}
		err = c.Write(ctx, 1, []byte(WsOp.ToString()))
		time.Sleep(1 * time.Second)
		if err != nil {
			log.Fatal("Error authenticate websocket (sending key): ", err)
			cancel()
		}

	}

	// send subscription string
	err = c.Write(ctx, 1, []byte(cfg.WsOp.ToString()))

	if err != nil {
		log.Fatal("Error sending Op to websocket: ", err)
	}

	doneC = make(chan struct{})
	stopC = make(chan struct{})

	go func() {
		// This function will exit either on error from
		// websocket.Conn.ReadMessage or when the stopC channel is
		// closed by the client.
		defer close(doneC)
		defer cancel()
		if WebsocketKeepalive {
			go keepAlive(ctx, c, WebsocketTimeout)
		}
		// Wait for the stopC channel to be closed.  We do that in a
		// separate goroutine because ReadMessage is a blocking
		// operation.
		silent := false
		go func() {
			select {
			case <-stopC:
				silent = true
			case <-doneC:
			}
			_ = c.Close(websocket.StatusNormalClosure, "normal closure")
		}()
		for {
			_, message, readErr := c.Read(ctx)
			//fmt.Println(string(message))
			if readErr != nil {
				if !silent {
					errHandler(readErr)
				}
				return
			}
			handler(message)
		}
	}()
	return
}

func keepAlive(ctx context.Context, c *websocket.Conn, d time.Duration) {
	t := time.NewTimer(d)
	defer t.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-t.C:
		}

		err := c.Ping(ctx)
		if err != nil {
			return
		}

		t.Reset(d)
	}
}
