package okex

import (
	"context"
	"encoding/json"
	"net/http"
)

// GetTickersService
type GetTickersService struct {
	c        *Client
	instType string
	uly      *string
}

// Set instrument type
func (s *GetTickersService) InstrumentType(instType string) *GetTickersService {
	s.instType = instType
	return s
}

// Set underlying
func (s *GetTickersService) Underlying(uly string) *GetTickersService {
	s.uly = &uly
	return s
}

// Do send request
func (s *GetTickersService) Do(ctx context.Context, opts ...RequestOption) (res *GetTickerServiceResponse, err error) {
	r := &request{
		method:   http.MethodGet,
		endpoint: "/api/v5/market/tickers",
	}

	r.setParam("instType", s.instType)

	if s.uly != nil {
		r.setParam("uly", *s.uly)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(GetTickerServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// GetTickerService
type GetTickerService struct {
	c      *Client
	instId string
}

// Set instrument type
func (s *GetTickerService) InstrumentId(instId string) *GetTickerService {
	s.instId = instId
	return s
}

// Do send request
func (s *GetTickerService) Do(ctx context.Context, opts ...RequestOption) (res *GetTickerServiceResponse, err error) {
	r := &request{
		method:   http.MethodGet,
		endpoint: "/api/v5/market/ticker",
	}

	r.setParam("instId", s.instId)

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(GetTickerServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to GetTrickersService and GetTickerService
type GetTickerServiceResponse struct {
	Code string          `json:"code"`
	Msg  string          `json:"msg"`
	Data []*TickerDetail `json:"data"`
}

type TickerDetail struct {
	InstType  string `json:"instType"`
	InstId    string `json:"instId"`
	Last      string `json:"last"`
	LastSz    string `json:"lastSz"`
	AskPx     string `json:"askPx"`
	AskSz     string `json:"askSz"`
	BidPx     string `json:"bidPx"`
	BidSz     string `json:"bidSz"`
	Open24h   string `json:"open24h"`
	High24h   string `json:"high24h"`
	Low24h    string `json:"low24h"`
	VolCcy24h string `json:"volCcy24h"`
	Vol24h    string `json:"vol24h"`
	SodUtc0   string `json:"sodUtc0"`
	SodUtc8   string `json:"sodUtc8"`
	Ts        string `json:"ts"`
}
