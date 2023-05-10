package market

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/fcamel/golang-practice/utils"
	"github.com/gorilla/websocket"
	"log"
	"strings"
	"time"
)

var huoBiUrl = "wss://api.huobi.pro/ws"

const huobiPingCheck int64 = 5
const huobiWsPingTimeout int64 = 10

type huoBiHandler struct {
	pingLastTime int64
}

func newHuoBi(ctx context.Context) *Worker {
	utils.Trace("")
	return &Worker{
		ctx:   ctx,
		wsUrl: huoBiUrl,
		handler: &huoBiHandler{
			pingLastTime: time.Now().Unix(),
		},
		Organize:         HuoBi,
		Status:           runIng,
		Subscribes:       make(map[string][]byte),
		Subscribing:      make(map[string][]byte),
		LastRunTimestamp: time.Duration(time.Now().UnixNano() / 1e6),
		WsConn:           nil,
		List:             newList(),
	}
}

func (h *huoBiHandler) formatSubscribeHandle(s *Subscriber) (b []byte) {
	utils.Trace("")
	switch s.MarketType {
	case SpotMarket:
		b = []byte(`{"id":"id1","sub":"market.` + s.Symbol + `.depth.step1"}`)
	case FuturesMarket:
	case OptionMarket:
	case WapMarket:
	}

	return
}

type huobiSubscriber struct {
	Status string `json:"status"`
	Subbed string `json:"subbed"`
}

func (h *huoBiHandler) subscribed(msg []byte, w *Worker) {
	utils.Trace("")
	subscribe := &huobiSubscriber{}
	json.Unmarshal(msg, subscribe)
	if subscribe.Status == "ok" {
		w.subscribed(strings.Split(subscribe.Subbed, ".")[1])
	}
}

func (h *huoBiHandler) pingPongHandle(w *Worker) {
	utils.Trace("")
	for {
		select {
		case <-time.NewTimer(time.Second * time.Duration(huobiPingCheck)).C:
			if (time.Now().Unix() - h.pingLastTime) > huobiWsPingTimeout {
				log.Printf("%s pingpong断线", HuoBi)
				w.closeRedialSub()
			} else {
				pong, _ := json.Marshal(struct {
					Pong time.Duration `json:"pong"`
				}{
					Pong: time.Duration(time.Now().UnixNano() / 1e6),
				})

				w.writeMessage(websocket.TextMessage, pong)
			}
		}
	}
}

func (h *huobiProvider) setSymbol() {
	utils.Trace("")
	h.Symbol = strings.Split(h.Ch, ".")[1]
}

func (h *huoBiHandler) formatMsgHandle(msgType int, msg []byte, w *Worker) (*Marketer, error) {
	utils.Trace("")
	switch msgType {
	case websocket.BinaryMessage:
		msg, err := gzipDecode(msg)
		if err != nil {
			return nil, err
		}

		market, err := h.marketerMsg(msg)

		if err == nil {
			return market, err
		}

		h.pongMsg(msg)
		h.subscribed(msg, w)
		return nil, nil
	default:
		return nil, nil
	}
}

type huobiProvider struct {
	Ch     string `json:"ch"`
	Symbol string
	Tick   struct {
		Bids      [][2]float64 `json:"bids"`
		Asks      [][2]float64 `json:"asks"`
		bidsDepth Depth
		asksDepth Depth
	} `json:"tick"`
	Timestamp time.Duration `json:"ts"`
}

func (h *huoBiHandler) marketerMsg(msg []byte) (*Marketer, error) {
	utils.Trace("")
	huobiData := &huobiProvider{}
	err := json.Unmarshal(msg, huobiData)
	if err != nil {
		return nil, err
	}
	if len(huobiData.Tick.Bids) == 0 || len(huobiData.Tick.Asks) == 0 {
		return nil, errors.New("序列化市场深度错误")
	}

	huobiData.Tick.bidsDepth = make(Depth, len(huobiData.Tick.Bids))
	huobiData.Tick.asksDepth = make(Depth, len(huobiData.Tick.Asks))
	huobiData.Tick.bidsDepth = huobiData.Tick.bidsDepth.formatFloat(huobiData.Tick.Bids)
	huobiData.Tick.asksDepth = huobiData.Tick.asksDepth.formatFloat(huobiData.Tick.Asks)
	huobiData.setSymbol()

	return h.newMarketer(huobiData)
}

func (h *huoBiHandler) newMarketer(p *huobiProvider) (*Marketer, error) {
	utils.Trace("")
	return &Marketer{
		Organize:  HuoBi,
		Symbol:    p.Symbol,
		BuyFirst:  p.Tick.bidsDepth[0][0],
		SellFirst: p.Tick.asksDepth[0][0],
		BuyDepth:  p.Tick.bidsDepth,
		SellDepth: p.Tick.asksDepth,
		Timestamp: p.Timestamp,
		Temporize: time.Duration(time.Now().UnixNano()/1e6) - p.Timestamp,
	}, nil
}

type huobiPing struct {
	Ping int64 `json:"ping"`
}

func (h *huoBiHandler) pongMsg(msg []byte) {
	utils.Trace("")
	huobiPing := &huobiPing{}
	json.Unmarshal(msg, huobiPing)
	if huobiPing.Ping != 0 {
		h.pingLastTime = time.Now().Unix()
	}
}
