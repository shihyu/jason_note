package model

import (
	"github.com/shopspring/decimal"
	"github.com/vx416/axs/pkg/utils"
	"gopkg.in/guregu/null.v4"
)

func NewInitBalanceChangeLog(
	eventID string,
	eventTypeID int64,
	idempotencyKey string,
	changeID int64,
	accountID int64,
	accountShardID int32,
	userID int64,
	currencyCode string,
	currencySymbol string,
	availableDelta string,
	frozeDelta string,
	fallbackCurrencyCode string,
	fallbackCurrencySymbol string,
	fallbackAvailableDelta string,
	fallbackFrozeDelta string,
	sourceSvcID int64,
	relatedOrderID int64,
	submittedMsec TimestampInMsec,
) (*BalanceChangeLog, error) {

	decimals, err := utils.DecimalFromString(availableDelta, frozeDelta)
	if err != nil {
		return nil, err
	}
	fallbackDecimals := []decimal.Decimal{decimal.Zero, decimal.Zero}
	if fallbackCurrencyCode != "" {
		fallbackDecimals, err = utils.DecimalFromString(fallbackAvailableDelta, fallbackFrozeDelta)
		if err != nil {
			return nil, err
		}
	}
	return &BalanceChangeLog{
		EventID:                eventID,
		EventTypeID:            eventTypeID,
		IdempotencyKey:         idempotencyKey,
		ChangeID:               changeID,
		Status:                 ChangeLogStatusInit,
		AccountID:              accountID,
		AccountShardID:         accountShardID,
		UserID:                 userID,
		CurrencyCode:           currencyCode,
		CurrencySymbol:         currencySymbol,
		AvailableDelta:         decimals[0],
		FrozenDelta:            decimals[1],
		FallbackCurrencyCode:   null.NewString(fallbackCurrencyCode, true),
		FallbackCurrencySymbol: null.NewString(fallbackCurrencySymbol, true),
		FallbackAvailableDelta: decimal.NewNullDecimal(fallbackDecimals[0]),
		FallbackFrozenDelta:    decimal.NewNullDecimal(fallbackDecimals[1]),
		SourceSvcID:            sourceSvcID,
		RelatedOrderID:         relatedOrderID,
		SubmittedMsec:          submittedMsec,
	}, nil
}

type BalanceChangeLog struct {
	ID                     int64               `db:"id"`
	EventID                string              `db:"event_id"`
	EventTypeID            int64               `db:"event_type_id"`
	IdempotencyKey         string              `db:"idempotency_key"`
	ChangeID               int64               `db:"change_id"`
	Status                 ChangeLogStatus     `db:"status"`
	AccountID              int64               `db:"account_id"`
	AccountShardID         int32               `db:"account_shard_id"`
	UserID                 int64               `db:"user_id"`
	CurrencyCode           string              `db:"currency_code"`
	CurrencySymbol         string              `db:"currency_symbol"`
	AvailableDelta         decimal.Decimal     `db:"available_delta"`
	FrozenDelta            decimal.Decimal     `db:"frozen_delta"`
	FallbackCurrencyCode   null.String         `db:"fallback_currency_code"`
	FallbackCurrencySymbol null.String         `db:"fallback_currency_symbol"`
	FallbackAvailableDelta decimal.NullDecimal `db:"fallback_available_delta"`
	FallbackFrozenDelta    decimal.NullDecimal `db:"fallback_frozen_delta"`
	UseFallback            bool                `db:"use_fallback"`
	SourceSvcID            int64               `db:"source_svc_id"`
	RelatedOrderID         int64               `db:"related_order_id"`
	KafkaOffset            int64               `db:"kafka_offset"`
	KafkaPartition         int32               `db:"kafka_partition"`
	SubmittedMsec          TimestampInMsec     `db:"submitted_msec"`
	InsertMsec             TimestampInMsec     `db:"insert_msec"`
	UpdatedMsec            TimestampInMsec     `db:"updated_msec"`
	AckMsec                TimestampInMsec     `db:"ack_msec"`
	AckStatus              AckStatus           `db:"ack_status"`
	RejectReason           string              `db:"reject_reason"`
	CallbackStatus         ChangeLogStatus     `db:"callback_status"`
}

func NewEventApplyResult(eventID string, rejectReason string, changeID int64, idempotencyKey string, status ChangeLogStatus, accountID int64, shardID int32, userFallback bool) *EventApplyResult {
	return &EventApplyResult{
		EventID:        eventID,
		RejectReason:   rejectReason,
		ChangeID:       changeID,
		IdempotencyKey: idempotencyKey,
		Status:         status,
		AccountID:      accountID,
		ShardID:        shardID,
		UserFallback:   userFallback,
	}
}

type EventApplyResult struct {
	EventID        string
	RejectReason   string
	ChangeID       int64
	IdempotencyKey string
	Status         ChangeLogStatus
	AccountID      int64
	ShardID        int32
	UserFallback   bool
}
