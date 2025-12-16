package factory

import (
	"github.com/shopspring/decimal"
	"github.com/vx416/axs/pkg/model"
	gofactory "github.com/vx416/gogo-factory"
	"github.com/vx416/gogo-factory/attr"
	"github.com/vx416/gogo-factory/genutil"
)

type AccountBalanceChangeFactory struct {
	*gofactory.Factory
}

var AccountBalanceChange = &AccountBalanceChangeFactory{gofactory.New(
	&model.AccountBalanceChange{},
	attr.Int("AccountID", genutil.SeqInt(1, 1)),
	attr.Int("UserID", genutil.SeqInt(1, 1)),
	attr.Int("ShardID", genutil.SeqInt(1, 1)),
	attr.Attr("CurrencyCode", genutil.FixInterface(nil)),
	attr.Str("AvailableDelta", genutil.FixStr("100.1")),
	attr.Str("FrozenDelta", genutil.FixStr("100.1")),
	attr.Bool("NotExist", genutil.RandBool(1)),
)}

type WriteAccountFactory struct {
	*gofactory.Factory
}

var WriteAccount = &WriteAccountFactory{gofactory.New(
	&model.WriteAccount{},
	attr.Int("AccountID", genutil.SeqInt(1, 1)),
	attr.Int("UserID", genutil.SeqInt(1, 1)),
	attr.Int("ShardID", genutil.SeqInt(1, 1)),
	attr.Attr("BalanceChangesMap", genutil.FixInterface(nil)),
)}

func (f WriteAccountFactory) WithAccInfo(accID, shardID, userID int, currencies []string, availableDeltaRange []int, frozeDeltaRange []int) *WriteAccountFactory {
	balanceChangesMap := make(map[model.CurrencyCode]model.AccountBalanceChange)
	for _, currency := range currencies {
		availableDelta := genutil.RandInt(availableDeltaRange[0], availableDeltaRange[1])()
		frozenDelta := genutil.RandInt(frozeDeltaRange[0], frozeDeltaRange[1])()
		balanceChangesMap[model.CurrencyCode(currency)] = model.AccountBalanceChange{
			AccountID:      int64(accID),
			UserID:         int64(userID),
			ShardID:        int32(shardID),
			CurrencyCode:   model.CurrencyCode(currency),
			AvailableDelta: decimal.NewFromInt(int64(availableDelta)),
			FrozenDelta:    decimal.NewFromInt(int64(frozenDelta)),
			NotExist:       false,
		}
	}

	return &WriteAccountFactory{f.Attrs(
		attr.Int("AccountID", genutil.FixInt(accID)),
		attr.Int("UserID", genutil.FixInt(userID)),
		attr.Int("ShardID", genutil.FixInt(shardID)),
		attr.Attr("BalanceChangesMap", genutil.FixInterface(balanceChangesMap)),
	)}
}

func (f WriteAccountFactory) BuildSeqUserID(start, end int, shardID int, currencies []string, availableDeltaRange []int, frozeDeltaRange []int) map[int64]*model.WriteAccount {
	result := make(map[int64]*model.WriteAccount)
	for start <= end {
		userID := start
		writeAccount := f.WithAccInfo(userID, shardID, userID, currencies, availableDeltaRange, frozeDeltaRange).MustBuild().(*model.WriteAccount)
		result[int64(userID)] = writeAccount
		start++
	}
	return result
}
