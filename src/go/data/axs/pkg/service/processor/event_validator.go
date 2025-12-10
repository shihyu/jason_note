package processor

import (
	"context"

	"github.com/pkg/errors"
	"github.com/shopspring/decimal"
	"github.com/vx416/axs/pb/eventpb"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/service/svcerr"
	"google.golang.org/protobuf/proto"
)

func NewChangeDecimal(change *eventpb.BalanceChange) (ChangeDecimal, error) {
	availableDelta, err := decimal.NewFromString(change.AvailableDelta)
	if err != nil {
		return ChangeDecimal{}, err
	}
	frozenDelta, err := decimal.NewFromString(change.FrozenDelta)
	if err != nil {
		return ChangeDecimal{}, err
	}
	fallbackAvailableDelta := decimal.Zero
	if change.FallbackAvailableDelta != "" {
		fallbackAvailableDelta, err = decimal.NewFromString(change.FallbackAvailableDelta)
		if err != nil {
			return ChangeDecimal{}, err
		}
	}
	fallbackFrozenDelta := decimal.Zero
	if change.FallbackFrozenDelta != "" {
		fallbackFrozenDelta, err = decimal.NewFromString(change.FallbackFrozenDelta)
		if err != nil {
			return ChangeDecimal{}, err
		}
	}
	return ChangeDecimal{
		ChangeId:               change.ChangeId,
		CurrencyCode:           change.CurrencyCode,
		AvailableDelta:         availableDelta,
		FrozenDelta:            frozenDelta,
		FallbackCurrencyCode:   change.FallbackCurrencyCode,
		FallbackAvailableDelta: fallbackAvailableDelta,
		FallbackFrozenDelta:    fallbackFrozenDelta,
	}, nil
}

type ChangeDecimal struct {
	ChangeId       int64
	CurrencyCode   string
	AvailableDelta decimal.Decimal
	FrozenDelta    decimal.Decimal

	FallbackCurrencyCode   string
	FallbackAvailableDelta decimal.Decimal
	FallbackFrozenDelta    decimal.Decimal
	ApplyFallback          bool
}

type DecodedEvent struct {
	Msg            mq.ConsumedMessage
	Event          *eventpb.BalanceChangeEvent
	ChangeDecimals []*ChangeDecimal
}

type EventValidatorRepository interface {
	GetIdempotencyKeysStatus(ctx context.Context, keys []string) (map[string]model.ChangeLogStatus, error)
}

type EventValidator struct {
	cacheRepo domain.CacheRepository
}

// BatchEvents holds the result of decoding events
type BatchEvents struct {
	NewEvents       []*DecodedEvent
	ProcessedEvents []*DecodedEvent
	Total           int
}

func (ev EventValidator) DecodeEventsAndGroupByShardID(ctx context.Context, msgs []mq.ConsumedMessage) (shardIDBatchEvents map[int32]*BatchEvents, invalidFormatEvents []*eventpb.BalanceChangeEvent, err error) {
	allEvents, invalidEvents, err := ev.decodeEvents(ctx, msgs)
	if err != nil {
		return nil, nil, err
	}
	newEvents, processedEvents, err := ev.idempotencyCheck(ctx, allEvents)
	if err != nil {
		return nil, nil, err
	}

	shardIDBatchEvents = make(map[int32]*BatchEvents)
	for _, event := range newEvents {
		shardID := int32(event.Event.AccountShardId)
		if _, exists := shardIDBatchEvents[shardID]; !exists {
			shardIDBatchEvents[shardID] = &BatchEvents{
				NewEvents:       make([]*DecodedEvent, 0),
				ProcessedEvents: make([]*DecodedEvent, 0),
				Total:           0,
			}
		}
		shardIDBatchEvents[shardID].NewEvents = append(shardIDBatchEvents[shardID].NewEvents, event)
		shardIDBatchEvents[shardID].Total++
	}
	for _, event := range processedEvents {
		shardID := int32(event.Event.AccountShardId)
		if _, exists := shardIDBatchEvents[shardID]; !exists {
			shardIDBatchEvents[shardID] = &BatchEvents{
				NewEvents:       make([]*DecodedEvent, 0),
				ProcessedEvents: make([]*DecodedEvent, 0),
				Total:           0,
			}
		}
		shardIDBatchEvents[shardID].ProcessedEvents = append(shardIDBatchEvents[shardID].ProcessedEvents, event)
		shardIDBatchEvents[shardID].Total++
	}

	return shardIDBatchEvents, invalidEvents, nil
}

func (ev EventValidator) decodeEvents(ctx context.Context, msgs []mq.ConsumedMessage) (decodeEvents []*DecodedEvent, invalidFormatEvents []*eventpb.BalanceChangeEvent, err error) {
	events := make([]*DecodedEvent, 0, len(msgs))
	invalidFormatEvents = make([]*eventpb.BalanceChangeEvent, 0, len(msgs))
	invalidMsgs := make([]mq.ConsumedMessage, 0)
	for _, msg := range msgs {
		u := proto.UnmarshalOptions{
			AllowPartial: true,
			Merge:        true,
		}
		event := &eventpb.BalanceChangeEvent{}
		err := u.Unmarshal(msg.GetPayload(), event)
		if err != nil {
			logger.GetLogger(mq.LogWithMessage(ctx, msg)).Error().Err(err).Msg("failed to unmarshal balance change event")
			invalidMsgs = append(invalidMsgs, msg)
			continue
		}
		decodedEvent, err := ev.validAndDecodeEvent(ctx, msg, event)
		if err != nil {
			logger.GetLogger(mq.LogWithMessage(ctx, msg)).Error().Err(err).Msg("invalid balance change event format")
			invalidFormatEvents = append(invalidFormatEvents, event)
			continue
		}
		logger.GetLogger(mq.LogWithMessage(ctx, msg)).Debug().Msg("successfully decoded balance change event")
		events = append(events, decodedEvent)
	}
	if len(invalidMsgs) > 0 {
		ev.processCannotParsedMessages(context.Background(), invalidMsgs)
	}
	return events, invalidFormatEvents, nil
}

// idempotency check
func (ev EventValidator) idempotencyCheck(ctx context.Context, events []*DecodedEvent) (newEvents, processedEvents []*DecodedEvent, err error) {
	keys := make([]string, 0, len(events))
	for _, de := range events {
		keys = append(keys, de.Event.IdempotencyKey)
	}
	shardID := int32(events[0].Event.AccountShardId)
	keyStatus, err := ev.cacheRepo.GetIdempotencyKeysStatus(ctx, keys, shardID)
	if err != nil {
		return nil, nil, svcerr.NewNeedRetryError(err)
	}
	newEvents = make([]*DecodedEvent, 0, len(events))
	for _, event := range events {
		if status, exists := keyStatus[event.Event.IdempotencyKey]; exists && status.IsFinalStatus() {
			logger.GetLogger(mq.LogWithMessage(ctx, event.Msg)).Warn().Str("idemKey", event.Event.IdempotencyKey).Msgf("event already processed with status: %d", status)
			processedEvents = append(processedEvents, event)
			continue
		}
		logger.GetLogger(mq.LogWithMessage(ctx, event.Msg)).Debug().Msg("event is new and will be processed")
		newEvents = append(newEvents, event)
	}

	return newEvents, processedEvents, nil
}

func (ev EventValidator) processCannotParsedMessages(ctx context.Context, msgs []mq.ConsumedMessage) {
	// TODO: send to dead letter queue
}

func (ev EventValidator) validAndDecodeEvent(ctx context.Context, msg mq.ConsumedMessage, event *eventpb.BalanceChangeEvent) (*DecodedEvent, error) {
	if event.IdempotencyKey == "" {
		return nil, errors.New("missing idempotency key")
	}
	if event.AccountShardId < 0 {
		return nil, errors.New("invalid account shard ID")
	}
	if event.AccountId <= 0 {
		return nil, errors.New("invalid account ID")
	}
	if event.SourceService == "" {
		return nil, errors.New("missing source service")
	}
	if event.RelatedOrderId < 0 {
		return nil, errors.New("invalid related order ID")
	}
	if len(event.Changes) == 0 {
		return nil, errors.New("no balance changes in event")
	}
	changeDecimals := make([]*ChangeDecimal, 0, len(event.Changes))
	for _, change := range event.Changes {
		if change.ChangeId <= 0 {
			return nil, errors.New("invalid change ID in balance change")
		}
		if change.CurrencyCode == "" {
			return nil, errors.New("missing currency code in balance change")
		}
		changeDecimal, err := NewChangeDecimal(change)
		if err != nil {
			return nil, errors.WithMessage(err, "invalid balance change format")
		}
		changeDecimals = append(changeDecimals, &changeDecimal)
	}

	return &DecodedEvent{
		Msg:            msg,
		Event:          event,
		ChangeDecimals: changeDecimals,
	}, nil
}
