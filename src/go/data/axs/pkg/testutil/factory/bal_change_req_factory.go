package factory

import (
	"time"

	"github.com/vx416/axs/pb/apipb"
	gofactory "github.com/vx416/gogo-factory"
	"github.com/vx416/gogo-factory/attr"
	"github.com/vx416/gogo-factory/genutil"
)

type SubmitBalanceChangeRequestFactory struct {
	*gofactory.Factory
}

var SubmitBalanceChangeRequest = &SubmitBalanceChangeRequestFactory{gofactory.New(
	&apipb.SubmitBalanceChangeRequest{},
	attr.Str("EventId", genutil.RandUUID()),
	attr.Str("EventType", genutil.RandAlph(10)),
	attr.Int("EventTypeId", genutil.SeqInt(1, 1)),
	attr.Int("AccountId", genutil.SeqInt(1, 1)),
	attr.Int("UserId", genutil.SeqInt(1, 1)),
	attr.Str("SourceService", genutil.RandAlph(10)),
	attr.Int("SourceSvcId", genutil.SeqInt(1, 1)),
	attr.Int("RelatedOrderId", genutil.SeqInt(1, 1)),
	attr.Str("IdempotencyKey", genutil.RandUUID()),
	attr.Int("CreatedMsec", func() int {
		return int(time.Now().UnixMilli())
	}),
)}

func (f SubmitBalanceChangeRequestFactory) WithAccInfo(accID, userID int) *SubmitBalanceChangeRequestFactory {
	return &SubmitBalanceChangeRequestFactory{f.Attrs(
		attr.Int("AccountId", genutil.FixInt(accID)),
		attr.Int("UserId", genutil.FixInt(userID)),
	)}
}

type BalanceChangeRequestFactory struct {
	*gofactory.Factory
}

var BalanceChangeRequest = &BalanceChangeRequestFactory{gofactory.New(
	&apipb.BalanceChange{},
	attr.Int("ChangeId", genutil.SeqInt(1, 1)),
	attr.Str("CurrencyCode", genutil.RandStrSet("BTC", "ETH", "USDT", "USDC", "BNB", "SOL")),
	attr.Str("CurrencySymbol", genutil.RandStrSet("BTC", "ETH", "USDT", "USDC", "BNB", "SOL")),
	attr.Str("AvailableDelta", genutil.RandAlph(10)),
	attr.Str("FrozenDelta", genutil.RandAlph(10)),
)}

func (f BalanceChangeRequestFactory) WithCurrency(currencyCode, currencySymbol string) *BalanceChangeRequestFactory {
	return &BalanceChangeRequestFactory{f.Attrs(
		attr.Str("CurrencyCode", genutil.FixStr(currencyCode)),
		attr.Str("CurrencySymbol", genutil.FixStr(currencySymbol)),
	)}
}

func (f BalanceChangeRequestFactory) WithFallbackCurrency(currencyCode, currencySymbol, available, frozen string) *BalanceChangeRequestFactory {
	return &BalanceChangeRequestFactory{f.Attrs(
		attr.Str("FallbackCurrencyCode", genutil.FixStr(currencyCode)),
		attr.Str("FallbackCurrencySymbol", genutil.FixStr(currencySymbol)),
		attr.Str("FallbackAvailableDelta", genutil.FixStr(available)),
		attr.Str("FallbackFrozenDelta", genutil.FixStr(frozen)),
	)}
}

func (f BalanceChangeRequestFactory) WithDelta(available, frozen string) *BalanceChangeRequestFactory {
	return &BalanceChangeRequestFactory{f.Attrs(
		attr.Str("AvailableDelta", genutil.FixStr(available)),
		attr.Str("FrozenDelta", genutil.FixStr(frozen)),
	)}
}
