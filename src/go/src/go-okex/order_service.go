package okex

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"strconv"
)

// PlaceOrderService place a single order
type PlaceOrderService struct {
	c          *Client
	instId     string
	tdMode     TradeMode
	ccy        *string
	clOrdId    *string
	tag        *string
	side       SideType
	posSide    PositionSideType
	ordType    OrderType
	sz         string
	px         *string
	reduceOnly *bool
	tgtCcy     *string
}

// Set instrument Id
func (s *PlaceOrderService) InstrumentId(instId string) *PlaceOrderService {
	s.instId = instId
	return s
}

// Set trade mode
func (s *PlaceOrderService) TradeMode(tdMode TradeMode) *PlaceOrderService {
	s.tdMode = tdMode
	return s
}

// Set Currency
func (s *PlaceOrderService) Currency(ccy string) *PlaceOrderService {
	s.ccy = &ccy
	return s
}

// Set Client Order Id
func (s *PlaceOrderService) ClientOrderId(clOrdId string) *PlaceOrderService {
	s.clOrdId = &clOrdId
	return s
}

// Set Tag field
func (s *PlaceOrderService) Tag(tag string) *PlaceOrderService {
	s.tag = &tag
	return s
}

// Set side
func (s *PlaceOrderService) Side(side SideType) *PlaceOrderService {
	s.side = side
	return s
}

// Set position side
func (s *PlaceOrderService) PositionSide(posSide PositionSideType) *PlaceOrderService {
	s.posSide = posSide
	return s
}

// Set order type
func (s *PlaceOrderService) OrderType(ordType OrderType) *PlaceOrderService {
	s.ordType = ordType
	return s
}

// Set size
func (s *PlaceOrderService) Size(sz string) *PlaceOrderService {
	s.sz = sz
	return s
}

// Set Order Price
func (s *PlaceOrderService) OrderPrice(px string) *PlaceOrderService {
	s.px = &px
	return s
}

// Set ReduceOnly
func (s *PlaceOrderService) ReduceOnly(reduceOnly bool) *PlaceOrderService {
	s.reduceOnly = &reduceOnly
	return s
}

// Set Quantity Type
func (s *PlaceOrderService) TargetCurrency(tgtCcy string) *PlaceOrderService {
	s.tgtCcy = &tgtCcy
	return s
}

// Do send request
func (s *PlaceOrderService) Do(ctx context.Context, opts ...RequestOption) (res *PlaceOrderResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/order",
		secType:  secTypeSigned,
	}

	r.setBodyParam("instId", s.instId)
	r.setBodyParam("tdMode", string(s.tdMode))
	r.setBodyParam("side", string(s.side))
	r.setBodyParam("posSide", string(s.posSide))
	r.setBodyParam("ordType", string(s.ordType))
	r.setBodyParam("sz", s.sz)

	if s.ccy != nil {
		r.setBodyParam("ccy", *s.ccy)
	}
	if s.clOrdId != nil {
		r.setBodyParam("clOrdId", *s.clOrdId)
	}
	if s.tag != nil {
		r.setBodyParam("tag", *s.tag)
	}
	if s.px != nil {
		r.setBodyParam("px", *s.px)
	}
	if s.reduceOnly != nil {
		r.setBodyParam("reduceOnly", strconv.FormatBool(*s.reduceOnly))
	}
	if s.tgtCcy != nil {
		r.setBodyParam("tgtCcy", *s.tgtCcy)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(PlaceOrderResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to PlaceOrderService
type PlaceOrderResponse struct {
	Code string         `json:"code"`
	Msg  string         `json:"msg"`
	Data []*OrderDetail `json:"data"`
}

// CancelOrderService cancel an order
type CancelOrderService struct {
	c       *Client
	instId  string
	ordId   *string
	clOrdId *string
}

// Set instrument Id
func (s *CancelOrderService) InstrumentId(instId string) *CancelOrderService {
	s.instId = instId
	return s
}

// Set order Id
func (s *CancelOrderService) OrderId(ordId string) *CancelOrderService {
	s.ordId = &ordId
	return s
}

// Set client order Id
func (s *CancelOrderService) ClientOrderId(clOrdId string) *CancelOrderService {
	s.clOrdId = &clOrdId
	return s
}

// Do send request
func (s *CancelOrderService) Do(ctx context.Context, opts ...RequestOption) (res *CancelOrderResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/cancel-order",
		secType:  secTypeSigned,
	}

	r.setBodyParam("instId", s.instId)

	if s.ordId != nil {
		r.setBodyParam("ordId", *s.ordId)
	}
	if s.clOrdId != nil {
		r.setBodyParam("clOrdId", *s.clOrdId)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(CancelOrderResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to CancelOrderService
type CancelOrderResponse struct {
	Code string         `json:"code"`
	Msg  string         `json:"msg"`
	Data []*OrderDetail `json:"data"`
}

//Cancel Multiple orders service

type CancelOrder struct {
	InstId  string  `json:"instId"`
	OrdId   *string `json:"ordId,omitempty"`
	ClOrdId *string `json:"clOrdId,omitempty"`
}

type CancelMultipleOrdersService struct {
	c      *Client
	orders []CancelOrder
}

// Set orders list
func (s *CancelMultipleOrdersService) OrderList(orders []CancelOrder) *CancelMultipleOrdersService {
	s.orders = orders
	return s
}

// Do send request
func (s *CancelMultipleOrdersService) Do(ctx context.Context, opts ...RequestOption) (res *CancelMultipleOrdersResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/cancel-batch-orders",
		secType:  secTypeSigned,
	}

	postBody, _ := json.Marshal(s.orders)
	r.body = bytes.NewBuffer(postBody)

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(CancelMultipleOrdersResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to CancelMultipleOrdersService
type CancelMultipleOrdersResponse struct {
	Code string         `json:"code"`
	Msg  string         `json:"msg"`
	Data []*OrderDetail `json:"data"`
}

// OrderListService list of all open orders
type OrderListService struct {
	c        *Client
	instType *string
	uly      *string
	instId   *string
	ordType  *OrderType
	state    *string
	after    *string
	before   *string
	limit    *string
}

// Set intrument type
func (s *OrderListService) InstrumentType(instType string) *OrderListService {
	s.instType = &instType
	return s
}

// Set underlying
func (s *OrderListService) Underlying(uly string) *OrderListService {
	s.uly = &uly
	return s
}

// Set instrument id
func (s *OrderListService) InstrumentId(instId string) *OrderListService {
	s.instId = &instId
	return s
}

// Set order type
func (s *OrderListService) OrderType(ordType OrderType) *OrderListService {
	s.ordType = &ordType
	return s
}

// Set state
func (s *OrderListService) State(state string) *OrderListService {
	s.state = &state
	return s
}

// Set after
func (s *OrderListService) After(after string) *OrderListService {
	s.after = &after
	return s
}

// Set before
func (s *OrderListService) Before(before string) *OrderListService {
	s.before = &before
	return s
}

// Set limit
func (s *OrderListService) Limit(limit string) *OrderListService {
	s.limit = &limit
	return s
}

// Do send request
func (s *OrderListService) Do(ctx context.Context, opts ...RequestOption) (res *OrderListServiceResponse, err error) {
	r := &request{
		method:   http.MethodGet,
		endpoint: "/api/v5/trade/orders-pending",
		secType:  secTypeSigned,
	}

	// TODO these filters do not work!

	if s.instType != nil {
		r.setParam("instType", *s.instType)
	}
	if s.uly != nil {
		r.setParam("uly", *s.uly)
	}
	if s.instId != nil {
		r.setParam("instId", *s.instId)
	}
	if s.ordType != nil {
		r.setParam("ordType", string(*s.ordType))
	}
	if s.state != nil {
		r.setParam("state", *s.state)
	}
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
	res = new(OrderListServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to OrderListService
type OrderListServiceResponse struct {
	Code string             `json:"code"`
	Msg  string             `json:"msg"`
	Data []*OrderListDetail `json:"data"`
}

type OrderListDetail struct {
	AccFillSz   string `json:"accFillSz"`
	AvgPx       string `json:"avgPx"`
	CTime       string `json:"cTime"`
	Category    string `json:"category"`
	Ccy         string `json:"ccy"`
	ClOrdId     string `json:"clOrdId"`
	Fee         string `json:"fee"`
	FeeCcy      string `json:"feeCcy"`
	FillPx      string `json:"fillPx"`
	FillSz      string `json:"fillSz"`
	FillTime    string `json:"fillTime"`
	InstId      string `json:"instId"`
	InstType    string `json:"instType"`
	Lever       string `json:"lever"`
	OrdId       string `json:"ordId"`
	OrdType     string `json:"ordType"`
	Pnl         string `json:"pnl"`
	PosSide     string `json:"posSide"`
	Px          string `json:"px"`
	Rebate      string `json:"rebate"`
	RebateCcy   string `json:"rebateCcy"`
	Side        string `json:"side"`
	SlOrdPx     string `json:"slOrdPx"`
	SlTriggerPx string `json:"slTriggerPx"`
	State       string `json:"state"`
	Sz          string `json:"sz"`
	Tag         string `json:"tag"`
	TgtCcy      string `json:"tgtCcy"`
	TdMode      string `json:"tdMode"`
	TpOrdPx     string `json:"tpOrdPx"`
	TpTriggerPx string `json:"tpTriggerPx"`
	TradeId     string `json:"tradeId"`
	UTime       string `json:"uTime"`
}

// AmendOrderService edit a pending order
type AmendOrderService struct {
	c         *Client
	instId    string
	cxlOnFail *bool
	ordId     *string
	clOrdId   *string
	reqId     *string
	newSz     *string
	newPx     *string
}

// Set instrument id
func (s *AmendOrderService) InstrumentId(instId string) *AmendOrderService {
	s.instId = instId
	return s
}

// Set cancel on fail
func (s *AmendOrderService) CancelOnFail(cxlOnFail bool) *AmendOrderService {
	s.cxlOnFail = &cxlOnFail
	return s
}

// Set order Id
func (s *AmendOrderService) OrderId(ordId string) *AmendOrderService {
	s.ordId = &ordId
	return s
}

// Set client order Id
func (s *AmendOrderService) ClientOrderId(clOrdId string) *AmendOrderService {
	s.clOrdId = &clOrdId
	return s
}

// Set client request Id
func (s *AmendOrderService) ClientRequestId(reqId string) *AmendOrderService {
	s.reqId = &reqId
	return s
}

// Set size
func (s *AmendOrderService) Size(newSz string) *AmendOrderService {
	s.newSz = &newSz
	return s
}

// Set price
func (s *AmendOrderService) Price(newPx string) *AmendOrderService {
	s.newPx = &newPx
	return s
}

// Do send request
func (s *AmendOrderService) Do(ctx context.Context, opts ...RequestOption) (res *AmendOrderServiceResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/amend-order",
		secType:  secTypeSigned,
	}

	r.setBodyParam("instId", s.instId)

	if s.cxlOnFail != nil {
		r.setBodyParam("cxlOnFail", strconv.FormatBool(*s.cxlOnFail))
	}
	if s.ordId != nil {
		r.setBodyParam("ordId", *s.ordId)
	}
	if s.clOrdId != nil {
		r.setBodyParam("clOrdId", *s.clOrdId)
	}
	if s.reqId != nil {
		r.setBodyParam("reqId", *s.reqId)
	}
	if s.newSz != nil {
		r.setBodyParam("newSz", *s.newSz)
	}
	if s.newPx != nil {
		r.setBodyParam("newPx", *s.newPx)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(AmendOrderServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to AmendOrderService
type AmendOrderServiceResponse struct {
	Code string         `json:"code"`
	Msg  string         `json:"msg"`
	Data []*OrderDetail `json:"data"`
}

type OrderDetail struct {
	OrdId   string `json:"ordId"`
	ClOrdId string `json:"clOrdId"`
	Tag     string `json:"tag"`
	SCode   string `json:"sCode"`
	SMsg    string `json:"sMsg"`
	ReqId   string `json:"reqId"`
}

// Close position
type ClosePositionService struct {
	c       *Client
	instId  string
	posSide *string
	mgnMode string
	ccy     *string
}

// Set instrument id
func (s *ClosePositionService) InstrumentId(instId string) *ClosePositionService {
	s.instId = instId
	return s
}

// Set position side
func (s *ClosePositionService) PositionSide(posSide string) *ClosePositionService {
	s.posSide = &posSide
	return s
}

// Set margin mode
func (s *ClosePositionService) MarginMode(mgnMode string) *ClosePositionService {
	s.mgnMode = mgnMode
	return s
}

// Set currency
func (s *ClosePositionService) Currency(ccy string) *ClosePositionService {
	s.ccy = &ccy
	return s
}

// Do send request
func (s *ClosePositionService) Do(ctx context.Context, opts ...RequestOption) (res *ClosePositionServiceResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/close-position",
		secType:  secTypeSigned,
	}

	r.setBodyParam("instId", s.instId)
	r.setBodyParam("mgnMode", s.mgnMode)

	if s.posSide != nil {
		r.setBodyParam("posSide", *s.posSide)
	}
	if s.ccy != nil {
		r.setBodyParam("ccy", *s.ccy)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(ClosePositionServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to ClosePositionService
type ClosePositionServiceResponse struct {
	Code string                 `json:"code"`
	Msg  string                 `json:"msg"`
	Data []*ClosePositionDetail `json:"data"`
}

type ClosePositionDetail struct {
	InstId  string `json:"instId"`
	PosSide string `json:"posSide"`
}

// PlaceOrderService places a single order
type PlaceAlgoOrderService struct {
	c          *Client
	instId     string
	tdMode     TradeMode
	ccy        *string
	side       SideType
	posSide    *PositionSideType
	ordType    OrderType
	sz         string
	reduceOnly *bool
	tgtCcy     *string

	// Stop order
	tpTriggerPx *string
	tpOrdPx     *string
	slTriggerPx *string
	slOrdPx     *string

	// Trigger order
	triggerPx *string
	orderPx   *string

	// TODO Iceberg order

	// TODO TWAP order
}

// Set instrument Id
func (s *PlaceAlgoOrderService) InstrumentId(instId string) *PlaceAlgoOrderService {
	s.instId = instId
	return s
}

// Set trade mode
func (s *PlaceAlgoOrderService) TradeMode(tdMode TradeMode) *PlaceAlgoOrderService {
	s.tdMode = tdMode
	return s
}

// Set Currency
func (s *PlaceAlgoOrderService) Currency(ccy string) *PlaceAlgoOrderService {
	s.ccy = &ccy
	return s
}

// Set side
func (s *PlaceAlgoOrderService) Side(side SideType) *PlaceAlgoOrderService {
	s.side = side
	return s
}

// Set position side
func (s *PlaceAlgoOrderService) PositionSide(posSide PositionSideType) *PlaceAlgoOrderService {
	s.posSide = &posSide
	return s
}

// Set order type
func (s *PlaceAlgoOrderService) OrderType(ordType OrderType) *PlaceAlgoOrderService {
	s.ordType = ordType
	return s
}

// Set size
func (s *PlaceAlgoOrderService) Size(sz string) *PlaceAlgoOrderService {
	s.sz = sz
	return s
}

// Set ReduceOnly
func (s *PlaceAlgoOrderService) ReduceOnly(reduceOnly bool) *PlaceAlgoOrderService {
	s.reduceOnly = &reduceOnly
	return s
}

// Set Quantity Type
func (s *PlaceAlgoOrderService) QuantityType(tgtCcy string) *PlaceAlgoOrderService {
	s.tgtCcy = &tgtCcy
	return s
}

// Set take profit trigger price
func (s *PlaceAlgoOrderService) TakeProfitTriggerPrice(tpTriggerPx string) *PlaceAlgoOrderService {
	s.tpTriggerPx = &tpTriggerPx
	return s
}

// Set take profit order price
func (s *PlaceAlgoOrderService) TakeProfitOrderPrice(tpOrdPx string) *PlaceAlgoOrderService {
	s.tpOrdPx = &tpOrdPx
	return s
}

// Set stop loss trigger price
func (s *PlaceAlgoOrderService) StopLossTriggerPrice(slTriggerPx string) *PlaceAlgoOrderService {
	s.slTriggerPx = &slTriggerPx
	return s
}

// Set stop loss order price
func (s *PlaceAlgoOrderService) StopLossOrderPrice(slOrdPx string) *PlaceAlgoOrderService {
	s.slOrdPx = &slOrdPx
	return s
}

// Set trigger price
func (s *PlaceAlgoOrderService) TriggerPrice(triggerPx string) *PlaceAlgoOrderService {
	s.triggerPx = &triggerPx
	return s
}

// Set order price
func (s *PlaceAlgoOrderService) OrderPrice(orderPx string) *PlaceAlgoOrderService {
	s.orderPx = &orderPx
	return s
}

// Do send request
func (s *PlaceAlgoOrderService) Do(ctx context.Context, opts ...RequestOption) (res *PlaceAlgoOrderServiceResponse, err error) {
	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/order-algo",
		secType:  secTypeSigned,
	}

	r.setBodyParam("instId", s.instId)
	r.setBodyParam("tdMode", string(s.tdMode))
	r.setBodyParam("side", string(s.side))
	r.setBodyParam("ordType", string(s.ordType))
	r.setBodyParam("sz", s.sz)

	if s.ccy != nil {
		r.setBodyParam("ccy", *s.ccy)
	}
	if s.posSide != nil {
		r.setBodyParam("posSide", string(*s.posSide))
	}
	if s.reduceOnly != nil {
		r.setBodyParam("reduceOnly", strconv.FormatBool(*s.reduceOnly))
	}
	if s.tgtCcy != nil {
		r.setBodyParam("tgtCcy", *s.tgtCcy)
	}
	if s.tpTriggerPx != nil {
		r.setBodyParam("tpTriggerPx", *s.tpTriggerPx)
	}
	if s.tpOrdPx != nil {
		r.setBodyParam("tpOrdPx", *s.tpOrdPx)
	}
	if s.slTriggerPx != nil {
		r.setBodyParam("slTriggerPx", *s.slTriggerPx)
	}
	if s.slOrdPx != nil {
		r.setBodyParam("slOrdPx", *s.slOrdPx)
	}
	if s.triggerPx != nil {
		r.setBodyParam("triggerPx", *s.triggerPx)
	}
	if s.orderPx != nil {
		r.setBodyParam("orderPx", *s.orderPx)
	}

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(PlaceAlgoOrderServiceResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to PlaceAlgoOrderService
type PlaceAlgoOrderServiceResponse struct {
	Code string             `json:"code"`
	Msg  string             `json:"msg"`
	Data []*AlgoOrderDetail `json:"data"`
}

// CancelAlgoOrderService cancel an algo order
type CancelAlgoOrderService struct {
	c      *Client
	algoId string
	instId string
}

// Set algo Id
func (s *CancelAlgoOrderService) AlgoId(algoId string) *CancelAlgoOrderService {
	s.algoId = algoId
	return s
}

// Set instrument Id
func (s *CancelAlgoOrderService) InstrumentId(instId string) *CancelAlgoOrderService {
	s.instId = instId
	return s
}

// Do send request
func (s *CancelAlgoOrderService) Do(ctx context.Context, opts ...RequestOption) (res *CancelAlgoOrderResponse, err error) {
	// TODO cancel multiple orders

	r := &request{
		method:   http.MethodPost,
		endpoint: "/api/v5/trade/cancel-algos",
		secType:  secTypeSigned,
	}

	r.setBodyParam("algoId", s.algoId)
	r.setBodyParam("instId", s.instId)

	data, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return nil, err
	}
	res = new(CancelAlgoOrderResponse)
	err = json.Unmarshal(data, res)
	if err != nil {
		return nil, err
	}
	return res, nil
}

// Response to CancelAlgoOrderService
type CancelAlgoOrderResponse struct {
	Code string             `json:"code"`
	Msg  string             `json:"msg"`
	Data []*AlgoOrderDetail `json:"data"`
}

type AlgoOrderDetail struct {
	AlgoId string `json:"algoId"`
	SCode  string `json:"sCode"`
	SMsg   string `json:"sMsg"`
}
