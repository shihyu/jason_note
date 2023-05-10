package market

import (
	"fmt"
	"github.com/fcamel/golang-practice/utils"
	"testing"
)

func Test_Run(t *testing.T) {
	utils.Trace("")
	Run()

	s := &Subscriber{
		Symbol:     "ETH-USDT",
		MarketType: SpotMarket,
		Organize:   OkEx,
	}
	WriteSubscribing <- s

	h := &Subscriber{
		Symbol:     "ethusdt",
		MarketType: SpotMarket,
		Organize:   HuoBi,
	}

	WriteSubscribing <- h

	for {
		select {
		case sub := <-ReadMarketPool:
			fmt.Println(sub)
		}
	}
}
