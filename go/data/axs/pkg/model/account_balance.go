package model

import "github.com/shopspring/decimal"

type AccountBalance struct {
	AccountID    int64           `db:"account_id"`
	UserID       int64           `db:"user_id"`
	CurrencyCode CurrencyCode    `db:"currency_code"`
	Available    decimal.Decimal `db:"available"`
	Frozen       decimal.Decimal `db:"frozen"`
	UpdatedMsec  TimestampInMsec `db:"updated_msec"`
	ShardID      int32           `db:"shard_id"`
	NotExist     bool            `db:"-"`
}

type Account struct {
	ID          int64           `db:"id"`
	UserID      int64           `db:"user_id"`
	ShardID     int32           `db:"shard_id"`
	CreatedMsec TimestampInMsec `db:"created_msec"`
}

type ListAccountBalancesOptions struct {
	AccountBalanceFilters []AccountBalanceFilter
}

func (opt *ListAccountBalancesOptions) AddFilter(accID int64, currencyDoe string, shardID int32) {
	filter := AccountBalanceFilter{
		AccountID:    accID,
		CurrencyCode: currencyDoe,
		ShardID:      shardID,
	}
	opt.AccountBalanceFilters = append(opt.AccountBalanceFilters, filter)
}

type AccountBalanceFilter struct {
	AccountID    int64
	CurrencyCode string
	ShardID      int32
}
