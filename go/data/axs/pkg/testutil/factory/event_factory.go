package factory

import (
	"strconv"
	"time"

	"github.com/vx416/axs/pb/eventpb"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	gofactory "github.com/vx416/gogo-factory"
	"github.com/vx416/gogo-factory/attr"
	"github.com/vx416/gogo-factory/genutil"
	"google.golang.org/protobuf/proto"
)

type BalanceChangeEventFactory struct {
	*gofactory.Factory
}

var BalanceChangeEvent = &BalanceChangeEventFactory{gofactory.New(
	&eventpb.BalanceChangeEvent{},
	attr.Str("EventId", genutil.RandUUID()),
	attr.Str("EventType", genutil.RandAlph(10)),
	attr.Int("EventTypeId", genutil.SeqInt(1, 1)),
	attr.Int("AccountId", genutil.SeqInt(1, 1)),
	attr.Int("UserId", genutil.SeqInt(1, 1)),
	attr.Int("AccountShardId", genutil.SeqInt(1, 1)),
	attr.Str("SourceService", genutil.RandAlph(5)),
	attr.Int("SourceSvcId", genutil.SeqInt(1, 1)),
	attr.Int("RelatedOrderId", genutil.SeqInt(1, 1)),
	attr.Str("IdempotencyKey", genutil.RandUUID()),
	attr.Int("CreatedMsec", func() int {
		return int(time.Now().UnixMilli())
	}),
)}

func (f BalanceChangeEventFactory) WithAccInfo(accID, userID, shardID int) *BalanceChangeEventFactory {
	return &BalanceChangeEventFactory{f.Attrs(
		attr.Int("AccountId", genutil.FixInt(accID)),
		attr.Int("UserId", genutil.FixInt(userID)),
		attr.Int("AccountShardId", genutil.FixInt(shardID)),
	)}
}

type BalanceChangeFactory struct {
	*gofactory.Factory
}

var BalanceChange = &BalanceChangeFactory{gofactory.New(
	&eventpb.BalanceChange{},
	attr.Int("ChangeId", genutil.SeqInt(1, 1)),
	attr.Str("CurrencyCode", genutil.RandStrSet("BTC", "ETH", "USDT", "USDC", "BNB", "SOL")),
	attr.Str("CurrencySymbol", genutil.RandStrSet("BTC", "ETH", "USDT", "USDC", "BNB", "SOL")),
	attr.Str("AvailableDelta", genutil.FixStr("100")),
	attr.Str("FrozenDelta", genutil.FixStr("100")),
)}

func (f BalanceChangeFactory) WithCurrency(currencyCode, currencySymbol string) *BalanceChangeFactory {
	return &BalanceChangeFactory{f.Attrs(
		attr.Str("CurrencyCode", genutil.FixStr(currencyCode)),
		attr.Str("CurrencySymbol", genutil.FixStr(currencySymbol)),
	)}
}

func (f BalanceChangeFactory) WithDelta(available, frozen string) *BalanceChangeFactory {
	return &BalanceChangeFactory{f.Attrs(
		attr.Str("AvailableDelta", genutil.FixStr(available)),
		attr.Str("FrozenDelta", genutil.FixStr(frozen)),
	)}
}

func (f BalanceChangeFactory) WithFallbackInfo(fallbackCurrencyCode, fallbackCurrencySymbol, fallbackAvailable, fallbackFrozen string) *BalanceChangeFactory {
	return &BalanceChangeFactory{f.Attrs(
		attr.Str("FallbackCurrencyCode", genutil.FixStr(fallbackCurrencyCode)),
		attr.Str("FallbackCurrencySymbol", genutil.FixStr(fallbackCurrencySymbol)),
		attr.Str("FallbackAvailableDelta", genutil.FixStr(fallbackAvailable)),
		attr.Str("FallbackFrozenDelta", genutil.FixStr(fallbackFrozen)),
	)}
}

func EventToMQMessage(event *eventpb.BalanceChangeEvent) (*mq.InMemoryConsumedMessage, error) {
	eventData, err := proto.Marshal(event)
	if err != nil {
		return &mq.InMemoryConsumedMessage{}, err
	}

	msgKey := []byte(strconv.Itoa(int(event.AccountShardId)))
	return mq.NewInMemoryConsumedMessage(msgKey, eventData), nil
}

func EventToChangeLog(event *eventpb.BalanceChangeEvent) ([]*model.BalanceChangeLog, error) {
	logs := make([]*model.BalanceChangeLog, 0, len(event.Changes))
	for _, change := range event.Changes {
		log, err := model.NewInitBalanceChangeLog(
			event.EventId,
			event.EventTypeId,
			event.IdempotencyKey,
			change.ChangeId,
			event.AccountId,
			event.AccountShardId,
			event.UserId,
			change.CurrencyCode,
			change.CurrencySymbol,
			change.AvailableDelta,
			change.FrozenDelta,
			change.FallbackCurrencyCode,
			change.FallbackCurrencySymbol,
			change.FallbackAvailableDelta,
			change.FallbackFrozenDelta,
			event.SourceSvcId,
			event.RelatedOrderId,
			model.TimestampInMsec(event.CreatedMsec),
		)
		if err != nil {
			return nil, err
		}
		log.Status = model.ChangeLogStatusInit // Directly mark as published for testing
		logs = append(logs, log)
	}
	return logs, nil
}
