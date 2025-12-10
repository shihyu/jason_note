package model

import (
	"github.com/shopspring/decimal"
)

type CurrencyCode string

type TimestampInMsec int64

const (
	BalanceDecimalPlaces = 18
)

func DecimalShiftToInt(d decimal.Decimal) int64 {
	intVal := d.Shift(BalanceDecimalPlaces).IntPart()
	return intVal
}

var (
	LeaderTTLSecond = 3 // seconds
)
