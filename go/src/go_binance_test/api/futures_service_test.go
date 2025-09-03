package binance

import (
	"github.com/fcamel/golang-practice/utils"
	"testing"

	"github.com/stretchr/testify/suite"
)

type futuresTransferTestSuite struct {
	baseTestSuite
}

func TestFuturesTransferService(t *testing.T) {
	utils.Trace("")
	suite.Run(t, new(futuresTransferTestSuite))
}

func (s *futuresTransferTestSuite) TestTransfer() {
	utils.Trace("")
	data := []byte(`{
		"tranId": 100000001
	}`)
	s.mockDo(data, nil)
	defer s.assertDo()
	asset := "BTC"
	amount := "1.000"
	transferType := FuturesTransferTypeToFutures
	s.assertReq(func(r *request) {
		e := newSignedRequest().setFormParams(params{
			"asset":  asset,
			"amount": amount,
			"type":   transferType,
		})
		s.assertRequestEqual(e, r)
	})
	res, err := s.client.NewFuturesTransferService().Asset(asset).
		Amount(amount).Type(transferType).Do(newContext())
	s.r().NoError(err)
	e := &TransactionResponse{
		TranID: 100000001,
	}
	s.assertTransactionResponseEqual(e, res)
}

func (s *futuresTransferTestSuite) assertTransactionResponseEqual(a, e *TransactionResponse) {
	utils.Trace("")
	s.r().Equal(a.TranID, e.TranID, "TranID")
}

func (s *futuresTransferTestSuite) TestListFuturesTransfer() {
	utils.Trace("")
	data := []byte(`{
		"rows": [
		  {
			"asset": "USDT",
			"tranId": 100000001,
			"amount": "40.84624400",
			"type": 1,
			"timestamp": 1555056425000,
			"status": "CONFIRMED"
		  }
		],
		"total": 1
	}`)
	s.mockDo(data, nil)
	defer s.assertDo()
	asset := "USDT"
	startTime := int64(1555056425000)
	s.assertReq(func(r *request) {
		e := newSignedRequest().setParams(params{
			"asset":     asset,
			"startTime": startTime,
		})
		s.assertRequestEqual(e, r)
	})
	res, err := s.client.NewListFuturesTransferService().Asset(asset).
		StartTime(startTime).Do(newContext())
	s.r().NoError(err)
	e := &FuturesTransferHistory{
		Rows: []FuturesTransfer{
			{
				Asset:     asset,
				TranID:    int64(100000001),
				Amount:    "40.84624400",
				Type:      1,
				Timestamp: int64(1555056425000),
				Status:    FuturesTransferStatusTypeConfirmed,
			},
		},
		Total: 1,
	}
	s.assertFuturesTransferHistoryEqual(e, res)
}

func (s *futuresTransferTestSuite) assertFuturesTransferHistoryEqual(e, a *FuturesTransferHistory) {
	utils.Trace("")
	s.r().Equal(e.Total, a.Total, "Total")
	s.r().Len(a.Rows, len(e.Rows))
	for i := range a.Rows {
		s.assertFuturesTransferEqual(e.Rows[i], a.Rows[i])
	}
}

func (s *futuresTransferTestSuite) assertFuturesTransferEqual(e, a FuturesTransfer) {
	utils.Trace("")
	r := s.r()
	r.Equal(e.Asset, a.Asset, "Asset")
	r.Equal(e.TranID, a.TranID, "TranID")
	r.Equal(e.Amount, a.Amount, "Amount")
	r.Equal(e.Type, a.Type, "Type")
	r.Equal(e.Timestamp, a.Timestamp, "Timestamp")
	r.Equal(e.Status, a.Status, "Status")
}
