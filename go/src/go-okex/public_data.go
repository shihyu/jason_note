package okex

import (
	"context"
	"encoding/json"
	"net/http"
)

// GetInstrumentsService
type GetInstrumentsService struct {
	c        *Client
	instType string
	uly      *string
	instId   *string
}

// Set instrument type
func (s *GetInstrumentsService) InstrumentType(instType string) *GetInstrumentsService {
	s.instType = instType
	return s
}

// Set underlying
func (s *GetInstrumentsService) Underlying(uly string) *GetInstrumentsService {
	s.uly = &uly
	return s
}

// Set instrument id
func (s *GetInstrumentsService) InstrumentId(instId string) *GetInstrumentsService {
	s.instId = &instId
	return s
}

// Do send request
func (s *GetInstrumentsService) Do(ctx context.Context, opts ...RequestOption) (res *GetInstrumentsServiceRespone, err error) {
	r := &request{
		method:   http.MethodGet,
		endpoint: "/api/v5/public/instruments",
	}

	r.setParam("instType", s.instType)

	if s.uly != nil {
		r.setParam("uly", *s.uly)
	}
	if s.instId != nil {
		r.setParam("instId", *s.instId)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(GetInstrumentsServiceRespone)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to GetInstrumentsService
type GetInstrumentsServiceRespone struct {
	Code string              `json:"code"`
	Msg  string              `json:"msg"`
	Data []*InstrumentDetail `json:"data"`
}

type InstrumentDetail struct {
	InstType  string `json:"instType"`
	InstId    string `json:"instId"`
	Uly       string `json:"uly"`
	Category  string `json:"category"`
	BaseCcy   string `json:"baseCcy"`
	QuoteCcy  string `json:"quoteCcy"`
	SettleCcy string `json:"settleCcy"`
	CtVal     string `json:"ctVal"`
	CtMult    string `json:"ctMult"`
	CtValCcy  string `json:"ctValCcy"`
	OptType   string `json:"optType"`
	Stk       string `json:"stk"`
	ListTime  string `json:"listTime"`
	ExpTime   string `json:"expTime"`
	Lever     string `json:"lever"`
	TickSz    string `json:"tickSz"`
	LotSz     string `json:"lotSz"`
	MinSz     string `json:"minSz"`
	CtType    string `json:"ctType"`
	Alias     string `json:"alias"`
	State     string `json:"state"`
}

// GetDeliveryExerciseHistoryService
type GetDeliveryExerciseHistoryService struct {
	c        *Client
	instType string
	uly      string
	after    *string
	before   *string
	limit    *string
}

// Set instrument type
func (s *GetDeliveryExerciseHistoryService) InstrumentType(instType string) *GetDeliveryExerciseHistoryService {
	s.instType = instType
	return s
}

// Set underlying
func (s *GetDeliveryExerciseHistoryService) Underlying(uly string) *GetDeliveryExerciseHistoryService {
	s.uly = uly
	return s
}

// Set after
func (s *GetDeliveryExerciseHistoryService) After(after string) *GetDeliveryExerciseHistoryService {
	s.after = &after
	return s
}

// Set before
func (s *GetDeliveryExerciseHistoryService) Before(before string) *GetDeliveryExerciseHistoryService {
	s.before = &before
	return s
}

// Set limit
func (s *GetDeliveryExerciseHistoryService) Limit(limit string) *GetDeliveryExerciseHistoryService {
	s.limit = &limit
	return s
}

// Do send request
func (s *GetDeliveryExerciseHistoryService) Do(ctx context.Context, opts ...RequestOption) (res *GetDeliveryExerciseHistoryServiceResponse, err error) {
	r := &request{
		method:   http.MethodGet,
		endpoint: "/api/v5/public/delivery-exercise-history",
	}

	r.setParam("instType", s.instType)
	r.setParam("uly", s.uly)

	if s.after != nil {
		r.setParam("after", *s.after)
	}
	if s.before != nil {
		r.setParam("before", *s.before)
	}
	if s.limit != nil {
		r.setParam("limit", *s.limit)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(GetDeliveryExerciseHistoryServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to GetInstrumentsService
type GetDeliveryExerciseHistoryServiceResponse struct {
	Code string               `json:"code"`
	Msg  string               `json:"msg"`
	Data []*DeliveryExcercise `json:"data"`
}

type DeliveryExcercise struct {
	Ts      string                     `json:"timestamp"`
	Details []*DeliveryExcerciseDetail `json:"details"`
}

type DeliveryExcerciseDetail struct {
	Type   string `json:"type"`
	InstId string `json:"instId"`
	Px     string `json:"px"`
}
