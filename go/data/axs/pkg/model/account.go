package model

import (
	"github.com/pkg/errors"
	"github.com/shopspring/decimal"
)

var (
	ErrCurrencyNotFound    = errors.New("currency not found in account")
	ErrInsufficientBalance = errors.New("insufficient balance")
)

func NewReadAccount(id int64, userID int64, shardID int32) *ReadAccount {
	return &ReadAccount{
		AccountID:          id,
		UserID:             userID,
		ShardID:            shardID,
		AccountBalancesMap: make(map[CurrencyCode]AccountBalanceView),
	}
}

type ReadAccount struct {
	AccountID          int64
	UserID             int64
	ShardID            int32
	AccountBalancesMap map[CurrencyCode]AccountBalanceView
}

func (a *ReadAccount) GetCurrencyBalance(currency CurrencyCode) (AccountBalanceView, bool) {
	balance, exists := a.AccountBalancesMap[currency]
	return balance, exists
}

func (a *ReadAccount) GetAvailableAmount(currency CurrencyCode) (decimal.Decimal, bool) {
	balance, exists := a.AccountBalancesMap[currency]
	return balance.Available, exists
}

func (a *ReadAccount) GetFrozenAmount(currency CurrencyCode) (decimal.Decimal, bool) {
	balance, exists := a.AccountBalancesMap[currency]
	return balance.Frozen, exists
}

func (a *ReadAccount) AddCurrencyBalance(currency CurrencyCode, available, frozen decimal.Decimal, notExist bool) {
	a.AccountBalancesMap[currency] = AccountBalanceView{
		AccountID:    a.AccountID,
		UserID:       a.UserID,
		ShardID:      a.ShardID,
		CurrencyCode: currency,
		Available:    available,
		Frozen:       frozen,
		NotExist:     notExist,
	}
}

func (a *ReadAccount) CurrencyBalanceIsNotExist(currency CurrencyCode) bool {
	currencyBalance, exists := a.AccountBalancesMap[currency]
	if !exists {
		return false
	}
	return currencyBalance.NotExist
}

func (a *ReadAccount) ApplyChange(currency CurrencyCode, availableDelta, frozenDelta decimal.Decimal) error {
	balance, exists := a.AccountBalancesMap[currency]
	if !exists {
		return errors.WithMessagef(ErrInsufficientBalance, "currency %s not found in account %d", currency, a.AccountID)
	}
	if availableDelta.IsNegative() && availableDelta.Abs().GreaterThan(balance.Available) {
		return errors.WithMessagef(ErrInsufficientBalance, "available balance %s insufficient for %s for currency %s in account %d", balance.Available, availableDelta, currency, a.AccountID)
	}
	if frozenDelta.IsNegative() && frozenDelta.Abs().GreaterThan(balance.Frozen) {
		return errors.WithMessagef(ErrInsufficientBalance, "frozen balance %s insufficient for %s for currency %s in account %d", balance.Frozen, frozenDelta, currency, a.AccountID)
	}

	balance.Available = balance.Available.Add(availableDelta)
	balance.Frozen = balance.Frozen.Add(frozenDelta)
	a.AccountBalancesMap[currency] = balance
	return nil
}

func (a *ReadAccount) RollbackChange(currency CurrencyCode, availableDelta, frozenDelta decimal.Decimal) error {
	balance, exists := a.AccountBalancesMap[currency]
	if !exists {
		return ErrCurrencyNotFound
	}

	balance.Available = balance.Available.Sub(availableDelta)
	balance.Frozen = balance.Frozen.Sub(frozenDelta)
	a.AccountBalancesMap[currency] = balance
	return nil
}

type AccountBalanceView struct {
	AccountID    int64
	UserID       int64
	ShardID      int32
	CurrencyCode CurrencyCode
	Available    decimal.Decimal
	Frozen       decimal.Decimal
	NotExist     bool
}

func NewWriteAccount(id int64, userID int64, shardID int32) *WriteAccount {
	return &WriteAccount{
		AccountID:         id,
		UserID:            userID,
		ShardID:           shardID,
		BalanceChangesMap: make(map[CurrencyCode]AccountBalanceChange),
	}
}

type WriteAccount struct {
	AccountID         int64
	UserID            int64
	ShardID           int32
	BalanceChangesMap map[CurrencyCode]AccountBalanceChange
}

func (a *WriteAccount) ApplyChange(currency CurrencyCode, availableDelta, frozenDelta decimal.Decimal, notExist bool) {
	change, exists := a.BalanceChangesMap[currency]
	if !exists {
		change = AccountBalanceChange{
			CurrencyCode:   currency,
			AvailableDelta: decimal.Zero,
			FrozenDelta:    decimal.Zero,
			ShardID:        a.ShardID,
			AccountID:      a.AccountID,
			UserID:         a.UserID,
			NotExist:       notExist,
		}
	}
	change.AvailableDelta = change.AvailableDelta.Add(availableDelta)
	change.FrozenDelta = change.FrozenDelta.Add(frozenDelta)
	change.NotExist = change.NotExist || notExist
	a.BalanceChangesMap[currency] = change
}

type AccountBalanceChange struct {
	AccountID      int64
	UserID         int64
	ShardID        int32
	CurrencyCode   CurrencyCode
	AvailableDelta decimal.Decimal
	FrozenDelta    decimal.Decimal
	NotExist       bool
}

func (ac AccountBalanceChange) IsAddOperation() bool {
	return ac.AvailableDelta.GreaterThanOrEqual(decimal.Zero) && ac.FrozenDelta.GreaterThanOrEqual(decimal.Zero)
}
