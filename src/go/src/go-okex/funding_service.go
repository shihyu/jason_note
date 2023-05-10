package okex

import (
	"context"
	"encoding/json"
	"net/http"
)

// Fund Transfer
// https://www.okex.com/docs-v5/en/#rest-api-funding-funds-transfer
type FundTransferService struct {
	c            *Client
	ccy          string
	amt          string
	from         string
	to           string
	subAcct      *string
	instId       *string
	toInstId     *string
	transferType *string
	loanTrans    *bool
}

// Set Currency
func (s *FundTransferService) Currency(ccy string) *FundTransferService {
	s.ccy = ccy
	return s
}

// Set Amount
func (s *FundTransferService) Amount(amt string) *FundTransferService {
	s.amt = amt
	return s
}

// Set From
func (s *FundTransferService) From(from string) *FundTransferService {
	s.from = from
	return s
}

// Set To
func (s *FundTransferService) To(to string) *FundTransferService {
	s.to = to
	return s
}

// Set SubAccount
func (s *FundTransferService) SubAccount(subAcct string) *FundTransferService {
	s.subAcct = &subAcct
	return s
}

// Set Instrument Id
func (s *FundTransferService) InstrumentId(instId string) *FundTransferService {
	s.instId = &instId
	return s
}

// Set To Instrument Id
func (s *FundTransferService) ToInstrumentId(toInstId string) *FundTransferService {
	s.toInstId = &toInstId
	return s
}

// Set Transfer Type
func (s *FundTransferService) TransferType(transferType string) *FundTransferService {
	s.transferType = &transferType
	return s
}

// Do send request
func (s *FundTransferService) Do(ctx context.Context, opts ...RequestOption) (res *FundTransferServiceResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/asset/transfer",
		secType:  secTypeSigned,
	}

	r.setBodyParam("ccy", s.ccy)
	r.setBodyParam("amt", s.amt)
	r.setBodyParam("from", s.from)
	r.setBodyParam("to", s.to)

	if s.subAcct != nil {
		r.setBodyParam("ccy", *s.subAcct)
	}

	if s.instId != nil {
		r.setBodyParam("instId", *s.instId)
	}
	if s.toInstId != nil {
		r.setBodyParam("toInstId", *s.toInstId)
	}
	if s.transferType != nil {
		r.setBodyParam("transferType", *s.transferType)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(FundTransferServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

type FundTransferServiceResponse struct {
	Code string                `json:"code"`
	Data []*FundTransferDetail `json:"data"`
	Msg  string                `json:"msg"`
}

type FundTransferDetail struct {
	TransId string `json:"transId"`
	Ccy     string `json:"ccy"`
	From    string `json:"from"`
	Amt     string `json:"amt"`
	To      string `json:"to"`
}
