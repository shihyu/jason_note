package Impl

import (
	"regexp"
)

const (
	MSG_NORMAL = iota
	MSG_JRPC
)

type Event int

/*
	EventID
*/
const (
	EVENT_UNKNOWN Event = iota
	EVENT_ERROR
	EVENT_PING
	EVENT_LOGIN

	EVENT_BOOK_INSTRUMENTS
	EVENT_STATUS
	EVENT_BOOK_TICKERS
	EVENT_BOOK_OPEN_INTEREST
	EVENT_BOOK_KLINE
	EVENT_BOOK_TRADE
	EVENT_BOOK_ESTIMATE_PRICE
	EVENT_BOOK_MARK_PRICE
	EVENT_BOOK_MARK_PRICE_CANDLE_CHART
	EVENT_BOOK_LIMIT_PRICE
	EVENT_BOOK_ORDER_BOOK
	EVENT_BOOK_ORDER_BOOK5
	EVENT_BOOK_ORDER_BOOK_TBT
	EVENT_BOOK_ORDER_BOOK50_TBT
	EVENT_BOOK_OPTION_SUMMARY
	EVENT_BOOK_FUND_RATE
	EVENT_BOOK_KLINE_INDEX
	EVENT_BOOK_INDEX_TICKERS

	EVENT_BOOK_ACCOUNT
	EVENT_BOOK_POSTION
	EVENT_BOOK_ORDER
	EVENT_BOOK_ALG_ORDER

	EVENT_PLACE_ORDER
	EVENT_PLACE_BATCH_ORDERS
	EVENT_CANCEL_ORDER
	EVENT_CANCEL_BATCH_ORDERS
	EVENT_AMEND_ORDER
	EVENT_AMEND_BATCH_ORDERS

	EVENT_BOOKED_DATA
	EVENT_DEPTH_DATA
)

var EVENT_TABLE = [][]interface{}{
	{EVENT_UNKNOWN, "unknown", ""},
	{EVENT_ERROR, "error", ""},
	{EVENT_PING, "ping", ""},
	{EVENT_LOGIN, "login", ""},

	{EVENT_BOOK_INSTRUMENTS, "instruments", "instruments"},
	{EVENT_STATUS, "status", "status"},
	{EVENT_BOOK_TICKERS, "tickers", "tickers"},
	{EVENT_BOOK_OPEN_INTEREST, "open-interest", "open-interest"},
	{EVENT_BOOK_KLINE, "candle", "candle"},
	{EVENT_BOOK_TRADE, "trades", "trades"},
	{EVENT_BOOK_ESTIMATE_PRICE, "estimated-price", "estimated-price"},
	{EVENT_BOOK_MARK_PRICE, "标记价格", "mark-price"},
	{EVENT_BOOK_MARK_PRICE_CANDLE_CHART, "mark-price-candle", "mark-price-candle"},
	{EVENT_BOOK_LIMIT_PRICE, "price-limit", "price-limit"},
	{EVENT_BOOK_ORDER_BOOK, "books", "books"},
	{EVENT_BOOK_ORDER_BOOK5, "books5", "books5"},
	{EVENT_BOOK_ORDER_BOOK_TBT, "books-l2-tbt", "books-l2-tbt"},
	{EVENT_BOOK_ORDER_BOOK50_TBT, "books50-l2-tbt", "books50-l2-tbt"},
	{EVENT_BOOK_OPTION_SUMMARY, "opt-summary", "opt-summary"},
	{EVENT_BOOK_FUND_RATE, "funding-rate", "funding-rate"},
	{EVENT_BOOK_KLINE_INDEX, "index-candle", "index-candle"},
	{EVENT_BOOK_INDEX_TICKERS, "index-tickers", "index-tickers"},

	{EVENT_BOOK_ACCOUNT, "account", "account"},
	{EVENT_BOOK_POSTION, "positions", "positions"},
	{EVENT_BOOK_ORDER, "orders", "orders"},
	{EVENT_BOOK_ALG_ORDER, "orders-algo", "orders-algo"},
	//{EVENT_BOOK_B_AND_P, "balance_and_position", "balance_and_position"},

	/*
		JRPC
	*/
	{EVENT_PLACE_ORDER, "order", "order"},
	{EVENT_PLACE_BATCH_ORDERS, "batch-orders", "batch-orders"},
	{EVENT_CANCEL_ORDER, "cancel-order", "cancel-order"},
	{EVENT_CANCEL_BATCH_ORDERS, "batch-cancel-orders", "batch-cancel-orders"},
	{EVENT_AMEND_ORDER, "amend-order", "amend-order"},
	{EVENT_AMEND_BATCH_ORDERS, "batch-amend-orders", "batch-amend-orders"},

	{EVENT_BOOKED_DATA, "", ""},
	{EVENT_DEPTH_DATA, "", ""},
}

func (e Event) String() string {
	for _, v := range EVENT_TABLE {
		eventId := v[0].(Event)
		if e == eventId {
			return v[1].(string)
		}
	}

	return ""
}

func (e Event) GetChannel(pd Period) string {

	channel := ""

	for _, v := range EVENT_TABLE {
		eventId := v[0].(Event)
		if e == eventId {
			channel = v[2].(string)
			break
		}
	}

	if channel == "" {
		return ""
	}

	return channel + string(pd)
}

func GetEventId(raw string) Event {
	evt := EVENT_UNKNOWN

	for _, v := range EVENT_TABLE {
		channel := v[2].(string)
		if raw == channel {
			evt = v[0].(Event)
			break
		}

		regexp := regexp.MustCompile(`^(.*)([1-9][0-9]?[\w])$`)
		substr := regexp.FindStringSubmatch(raw)

		if len(substr) >= 2 {
			if substr[1] == channel {
				evt = v[0].(Event)
				break
			}
		}
	}

	return evt
}

type Period string

const (
	PERIOD_1YEAR Period = "1Y"

	PERIOD_6Mon Period = "6M"
	PERIOD_3Mon Period = "3M"
	PERIOD_1Mon Period = "1M"

	PERIOD_1WEEK Period = "1W"

	PERIOD_5DAY Period = "5D"
	PERIOD_3DAY Period = "3D"
	PERIOD_2DAY Period = "2D"
	PERIOD_1DAY Period = "1D"

	PERIOD_12HOUR Period = "12H"
	PERIOD_6HOUR  Period = "6H"
	PERIOD_4HOUR  Period = "4H"
	PERIOD_2HOUR  Period = "2H"
	PERIOD_1HOUR  Period = "1H"

	PERIOD_30MIN Period = "30m"
	PERIOD_15MIN Period = "15m"
	PERIOD_5MIN  Period = "5m"
	PERIOD_3MIN  Period = "3m"
	PERIOD_1MIN  Period = "1m"

	PERIOD_NONE Period = ""
)

const (
	DEPTH_SNAPSHOT = "snapshot"
	DEPTH_UPDATE   = "update"
)
