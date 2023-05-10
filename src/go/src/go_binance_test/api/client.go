package binance

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"crypto/tls"
	"fmt"
	"github.com/fcamel/golang-practice/utils"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/adshao/go-binance/v2/common"
	"github.com/adshao/go-binance/v2/delivery"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/bitly/go-simplejson"
	jsoniter "github.com/json-iterator/go"
)

// SideType define side type of order
type SideType string

// OrderType define order type
type OrderType string

// TimeInForceType define time in force type of order
type TimeInForceType string

// NewOrderRespType define response JSON verbosity
type NewOrderRespType string

// OrderStatusType define order status type
type OrderStatusType string

// SymbolType define symbol type
type SymbolType string

// SymbolStatusType define symbol status type
type SymbolStatusType string

// SymbolFilterType define symbol filter type
type SymbolFilterType string

// UserDataEventType define spot user data event type
type UserDataEventType string

// MarginTransferType define margin transfer type
type MarginTransferType int

// MarginLoanStatusType define margin loan status type
type MarginLoanStatusType string

// MarginRepayStatusType define margin repay status type
type MarginRepayStatusType string

// FuturesTransferStatusType define futures transfer status type
type FuturesTransferStatusType string

// SideEffectType define side effect type for orders
type SideEffectType string

// FuturesTransferType define futures transfer type
type FuturesTransferType int

// TransactionType define transaction type
type TransactionType string

// LendingType define the type of lending (flexible saving, activity, ...)
type LendingType string

// StakingProduct define the staking product (locked staking, flexible defi staking, locked defi staking, ...)
type StakingProduct string

// StakingTransactionType define the staking transaction type (subscription, redemption, interest)
type StakingTransactionType string

// LiquidityOperationType define the type of adding/removing liquidity to a liquidity pool(COMBINATION, SINGLE)
type LiquidityOperationType string

// SwappingStatus define the status of swap when querying the swap history
type SwappingStatus int

// LiquidityRewardType define the type of reward we'd claim
type LiquidityRewardType int

// RewardClaimStatus define the status of claiming a reward
type RewardClaimStatus int

// Endpoints
const (
	baseAPIMainURL    = "https://api.binance.com"
	baseAPITestnetURL = "https://testnet.binance.vision"
)

// UseTestnet switch all the API endpoints from production to the testnet
var UseTestnet = false

// Redefining the standard package
var json = jsoniter.ConfigCompatibleWithStandardLibrary

// Global enums
const (
	SideTypeBuy  SideType = "BUY"
	SideTypeSell SideType = "SELL"

	OrderTypeLimit           OrderType = "LIMIT"
	OrderTypeMarket          OrderType = "MARKET"
	OrderTypeLimitMaker      OrderType = "LIMIT_MAKER"
	OrderTypeStopLoss        OrderType = "STOP_LOSS"
	OrderTypeStopLossLimit   OrderType = "STOP_LOSS_LIMIT"
	OrderTypeTakeProfit      OrderType = "TAKE_PROFIT"
	OrderTypeTakeProfitLimit OrderType = "TAKE_PROFIT_LIMIT"

	TimeInForceTypeGTC TimeInForceType = "GTC"
	TimeInForceTypeIOC TimeInForceType = "IOC"
	TimeInForceTypeFOK TimeInForceType = "FOK"

	NewOrderRespTypeACK    NewOrderRespType = "ACK"
	NewOrderRespTypeRESULT NewOrderRespType = "RESULT"
	NewOrderRespTypeFULL   NewOrderRespType = "FULL"

	OrderStatusTypeNew             OrderStatusType = "NEW"
	OrderStatusTypePartiallyFilled OrderStatusType = "PARTIALLY_FILLED"
	OrderStatusTypeFilled          OrderStatusType = "FILLED"
	OrderStatusTypeCanceled        OrderStatusType = "CANCELED"
	OrderStatusTypePendingCancel   OrderStatusType = "PENDING_CANCEL"
	OrderStatusTypeRejected        OrderStatusType = "REJECTED"
	OrderStatusTypeExpired         OrderStatusType = "EXPIRED"

	SymbolTypeSpot SymbolType = "SPOT"

	SymbolStatusTypePreTrading   SymbolStatusType = "PRE_TRADING"
	SymbolStatusTypeTrading      SymbolStatusType = "TRADING"
	SymbolStatusTypePostTrading  SymbolStatusType = "POST_TRADING"
	SymbolStatusTypeEndOfDay     SymbolStatusType = "END_OF_DAY"
	SymbolStatusTypeHalt         SymbolStatusType = "HALT"
	SymbolStatusTypeAuctionMatch SymbolStatusType = "AUCTION_MATCH"
	SymbolStatusTypeBreak        SymbolStatusType = "BREAK"

	SymbolFilterTypeLotSize          SymbolFilterType = "LOT_SIZE"
	SymbolFilterTypePriceFilter      SymbolFilterType = "PRICE_FILTER"
	SymbolFilterTypePercentPrice     SymbolFilterType = "PERCENT_PRICE"
	SymbolFilterTypeMinNotional      SymbolFilterType = "MIN_NOTIONAL"
	SymbolFilterTypeIcebergParts     SymbolFilterType = "ICEBERG_PARTS"
	SymbolFilterTypeMarketLotSize    SymbolFilterType = "MARKET_LOT_SIZE"
	SymbolFilterTypeMaxNumAlgoOrders SymbolFilterType = "MAX_NUM_ALGO_ORDERS"

	UserDataEventTypeOutboundAccountPosition UserDataEventType = "outboundAccountPosition"
	UserDataEventTypeBalanceUpdate           UserDataEventType = "balanceUpdate"
	UserDataEventTypeExecutionReport         UserDataEventType = "executionReport"
	UserDataEventTypeListStatus              UserDataEventType = "ListStatus"

	MarginTransferTypeToMargin MarginTransferType = 1
	MarginTransferTypeToMain   MarginTransferType = 2

	FuturesTransferTypeToFutures FuturesTransferType = 1
	FuturesTransferTypeToMain    FuturesTransferType = 2

	MarginLoanStatusTypePending   MarginLoanStatusType = "PENDING"
	MarginLoanStatusTypeConfirmed MarginLoanStatusType = "CONFIRMED"
	MarginLoanStatusTypeFailed    MarginLoanStatusType = "FAILED"

	MarginRepayStatusTypePending   MarginRepayStatusType = "PENDING"
	MarginRepayStatusTypeConfirmed MarginRepayStatusType = "CONFIRMED"
	MarginRepayStatusTypeFailed    MarginRepayStatusType = "FAILED"

	FuturesTransferStatusTypePending   FuturesTransferStatusType = "PENDING"
	FuturesTransferStatusTypeConfirmed FuturesTransferStatusType = "CONFIRMED"
	FuturesTransferStatusTypeFailed    FuturesTransferStatusType = "FAILED"

	SideEffectTypeNoSideEffect SideEffectType = "NO_SIDE_EFFECT"
	SideEffectTypeMarginBuy    SideEffectType = "MARGIN_BUY"
	SideEffectTypeAutoRepay    SideEffectType = "AUTO_REPAY"

	TransactionTypeDeposit  TransactionType = "0"
	TransactionTypeWithdraw TransactionType = "1"
	TransactionTypeBuy      TransactionType = "0"
	TransactionTypeSell     TransactionType = "1"

	LendingTypeFlexible LendingType = "DAILY"
	LendingTypeFixed    LendingType = "CUSTOMIZED_FIXED"
	LendingTypeActivity LendingType = "ACTIVITY"

	LiquidityOperationTypeCombination LiquidityOperationType = "COMBINATION"
	LiquidityOperationTypeSingle      LiquidityOperationType = "SINGLE"

	timestampKey  = "timestamp"
	signatureKey  = "signature"
	recvWindowKey = "recvWindow"

	StakingProductLockedStaking       = "STAKING"
	StakingProductFlexibleDeFiStaking = "F_DEFI"
	StakingProductLockedDeFiStaking   = "L_DEFI"

	StakingTransactionTypeSubscription = "SUBSCRIPTION"
	StakingTransactionTypeRedemption   = "REDEMPTION"
	StakingTransactionTypeInterest     = "INTEREST"

	SwappingStatusPending SwappingStatus = 0
	SwappingStatusDone    SwappingStatus = 1
	SwappingStatusFailed  SwappingStatus = 2

	RewardTypeTrading   LiquidityRewardType = 0
	RewardTypeLiquidity LiquidityRewardType = 1

	RewardClaimPending RewardClaimStatus = 0
	RewardClaimDone    RewardClaimStatus = 1
)

func currentTimestamp() int64 {
	utils.Trace("")
	return FormatTimestamp(time.Now())
}

// FormatTimestamp formats a time into Unix timestamp in milliseconds, as requested by Binance.
func FormatTimestamp(t time.Time) int64 {
	utils.Trace("")
	return t.UnixNano() / int64(time.Millisecond)
}

func newJSON(data []byte) (j *simplejson.Json, err error) {
	utils.Trace("")
	j, err = simplejson.NewJson(data)
	if err != nil {
		return nil, err
	}
	return j, nil
}

// getAPIEndpoint return the base endpoint of the Rest API according the UseTestnet flag
func getAPIEndpoint() string {
	utils.Trace("")
	if UseTestnet {
		return baseAPITestnetURL
	}
	return baseAPIMainURL
}

// NewClient initialize an API client instance with API key and secret key.
// You should always call this function before using this SDK.
// Services will be created by the form client.NewXXXService().
func NewClient(apiKey, secretKey string) *Client {
	utils.Trace("")
	return &Client{
		APIKey:     apiKey,
		SecretKey:  secretKey,
		BaseURL:    getAPIEndpoint(),
		UserAgent:  "Binance/golang",
		HTTPClient: http.DefaultClient,
		Logger:     log.New(os.Stderr, "Binance-golang ", log.LstdFlags),
	}
}

//NewProxiedClient passing a proxy url
func NewProxiedClient(apiKey, secretKey, proxyUrl string) *Client {
	utils.Trace("")
	proxy, err := url.Parse(proxyUrl)
	if err != nil {
		log.Fatal(err)
	}
	tr := &http.Transport{
		Proxy:           http.ProxyURL(proxy),
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &Client{
		APIKey:    apiKey,
		SecretKey: secretKey,
		BaseURL:   getAPIEndpoint(),
		UserAgent: "Binance/golang",
		HTTPClient: &http.Client{
			Transport: tr,
		},
		Logger: log.New(os.Stderr, "Binance-golang ", log.LstdFlags),
	}
}

// NewFuturesClient initialize client for futures API
func NewFuturesClient(apiKey, secretKey string) *futures.Client {
	utils.Trace("")
	return futures.NewClient(apiKey, secretKey)
}

// NewDeliveryClient initialize client for coin-M futures API
func NewDeliveryClient(apiKey, secretKey string) *delivery.Client {
	utils.Trace("")
	return delivery.NewClient(apiKey, secretKey)
}

type doFunc func(req *http.Request) (*http.Response, error)

// Client define API client
type Client struct {
	APIKey     string
	SecretKey  string
	BaseURL    string
	UserAgent  string
	HTTPClient *http.Client
	Debug      bool
	Logger     *log.Logger
	TimeOffset int64
	do         doFunc
}

func (c *Client) debug(format string, v ...interface{}) {
	if c.Debug {
		c.Logger.Printf(format, v...)
	}
}

func (c *Client) parseRequest(r *request, opts ...RequestOption) (err error) {
	utils.Trace("")
	// set request options from user
	for _, opt := range opts {
		opt(r)
	}
	err = r.validate()
	if err != nil {
		return err
	}

	fullURL := fmt.Sprintf("%s%s", c.BaseURL, r.endpoint)
	if r.recvWindow > 0 {
		r.setParam(recvWindowKey, r.recvWindow)
	}
	if r.secType == secTypeSigned {
		r.setParam(timestampKey, currentTimestamp()-c.TimeOffset)
	}
	queryString := r.query.Encode()
	body := &bytes.Buffer{}
	bodyString := r.form.Encode()
	header := http.Header{}
	if r.header != nil {
		header = r.header.Clone()
	}
	if bodyString != "" {
		header.Set("Content-Type", "application/x-www-form-urlencoded")
		body = bytes.NewBufferString(bodyString)
	}
	if r.secType == secTypeAPIKey || r.secType == secTypeSigned {
		header.Set("X-MBX-APIKEY", c.APIKey)
	}

	if r.secType == secTypeSigned {
		raw := fmt.Sprintf("%s%s", queryString, bodyString)
		mac := hmac.New(sha256.New, []byte(c.SecretKey))
		_, err = mac.Write([]byte(raw))
		if err != nil {
			return err
		}
		v := url.Values{}
		v.Set(signatureKey, fmt.Sprintf("%x", (mac.Sum(nil))))
		if queryString == "" {
			queryString = v.Encode()
		} else {
			queryString = fmt.Sprintf("%s&%s", queryString, v.Encode())
		}
	}
	if queryString != "" {
		fullURL = fmt.Sprintf("%s?%s", fullURL, queryString)
	}
	c.debug("full url: %s, body: %s", fullURL, bodyString)

	r.fullURL = fullURL
	r.header = header
	r.body = body
	return nil
}

func (c *Client) callAPI(ctx context.Context, r *request, opts ...RequestOption) (data []byte, err error) {
	utils.Trace("")
	err = c.parseRequest(r, opts...)
	if err != nil {
		return []byte{}, err
	}
	req, err := http.NewRequest(r.method, r.fullURL, r.body)
	if err != nil {
		return []byte{}, err
	}
	req = req.WithContext(ctx)
	req.Header = r.header
	c.debug("request: %#v", req)
	f := c.do
	if f == nil {
		f = c.HTTPClient.Do
	}
	res, err := f(req)
	if err != nil {
		return []byte{}, err
	}
	data, err = ioutil.ReadAll(res.Body)
	if err != nil {
		return []byte{}, err
	}
	defer func() {
		cerr := res.Body.Close()
		// Only overwrite the retured error if the original error was nil and an
		// error occurred while closing the body.
		if err == nil && cerr != nil {
			err = cerr
		}
	}()
	c.debug("response: %#v", res)
	c.debug("response body: %s", string(data))
	c.debug("response status code: %d", res.StatusCode)

	if res.StatusCode >= http.StatusBadRequest {
		apiErr := new(common.APIError)
		e := json.Unmarshal(data, apiErr)
		if e != nil {
			c.debug("failed to unmarshal json: %s", e)
		}
		return nil, apiErr
	}
	return data, nil
}

// NewPingService init ping service
func (c *Client) NewPingService() *PingService {
	utils.Trace("")
	return &PingService{c: c}
}

// NewServerTimeService init server time service
func (c *Client) NewServerTimeService() *ServerTimeService {
	utils.Trace("")
	return &ServerTimeService{c: c}
}

// NewSetServerTimeService init set server time service
func (c *Client) NewSetServerTimeService() *SetServerTimeService {
	utils.Trace("")
	return &SetServerTimeService{c: c}
}

// NewDepthService init depth service
func (c *Client) NewDepthService() *DepthService {
	utils.Trace("")
	return &DepthService{c: c}
}

// NewAggTradesService init aggregate trades service
func (c *Client) NewAggTradesService() *AggTradesService {
	utils.Trace("")
	return &AggTradesService{c: c}
}

// NewRecentTradesService init recent trades service
func (c *Client) NewRecentTradesService() *RecentTradesService {
	utils.Trace("")
	return &RecentTradesService{c: c}
}

// NewKlinesService init klines service
func (c *Client) NewKlinesService() *KlinesService {
	utils.Trace("")
	return &KlinesService{c: c}
}

// NewListPriceChangeStatsService init list prices change stats service
func (c *Client) NewListPriceChangeStatsService() *ListPriceChangeStatsService {
	utils.Trace("")
	return &ListPriceChangeStatsService{c: c}
}

// NewListPricesService init listing prices service
func (c *Client) NewListPricesService() *ListPricesService {
	utils.Trace("")
	return &ListPricesService{c: c}
}

// NewListBookTickersService init listing booking tickers service
func (c *Client) NewListBookTickersService() *ListBookTickersService {
	utils.Trace("")
	return &ListBookTickersService{c: c}
}

// NewListSymbolTickerService init listing symbols tickers
func (c *Client) NewListSymbolTickerService() *ListSymbolTickerService {
	utils.Trace("")
	return &ListSymbolTickerService{c: c}
}

// NewCreateOrderService init creating order service
func (c *Client) NewCreateOrderService() *CreateOrderService {
	utils.Trace("")
	return &CreateOrderService{c: c}
}

// NewCreateOCOService init creating OCO service
func (c *Client) NewCreateOCOService() *CreateOCOService {
	utils.Trace("")
	return &CreateOCOService{c: c}
}

// NewCancelOCOService init cancel OCO service
func (c *Client) NewCancelOCOService() *CancelOCOService {
	utils.Trace("")
	return &CancelOCOService{c: c}
}

// NewGetOrderService init get order service
func (c *Client) NewGetOrderService() *GetOrderService {
	utils.Trace("")
	return &GetOrderService{c: c}
}

// NewCancelOrderService init cancel order service
func (c *Client) NewCancelOrderService() *CancelOrderService {
	utils.Trace("")
	return &CancelOrderService{c: c}
}

// NewCancelOpenOrdersService init cancel open orders service
func (c *Client) NewCancelOpenOrdersService() *CancelOpenOrdersService {
	utils.Trace("")
	return &CancelOpenOrdersService{c: c}
}

// NewListOpenOrdersService init list open orders service
func (c *Client) NewListOpenOrdersService() *ListOpenOrdersService {
	utils.Trace("")
	return &ListOpenOrdersService{c: c}
}

// NewListOpenOcoService init list open oco service
func (c *Client) NewListOpenOcoService() *ListOpenOcoService {
	utils.Trace("")
	return &ListOpenOcoService{c: c}
}

// NewListOrdersService init listing orders service
func (c *Client) NewListOrdersService() *ListOrdersService {
	utils.Trace("")
	return &ListOrdersService{c: c}
}

// NewGetAccountService init getting account service
func (c *Client) NewGetAccountService() *GetAccountService {
	utils.Trace("")
	return &GetAccountService{c: c}
}

// NewGetAPIKeyPermission init getting API key permission
func (c *Client) NewGetAPIKeyPermission() *GetAPIKeyPermission {
	utils.Trace("")
	return &GetAPIKeyPermission{c: c}
}

// NewListSavingsFlexibleProductsService get flexible products list (Savings)
func (c *Client) NewListSavingsFlexibleProductsService() *ListSavingsFlexibleProductsService {
	utils.Trace("")
	return &ListSavingsFlexibleProductsService{c: c}
}

// NewPurchaseSavingsFlexibleProductService purchase a flexible product (Savings)
func (c *Client) NewPurchaseSavingsFlexibleProductService() *PurchaseSavingsFlexibleProductService {
	utils.Trace("")
	return &PurchaseSavingsFlexibleProductService{c: c}
}

// NewRedeemSavingsFlexibleProductService redeem a flexible product (Savings)
func (c *Client) NewRedeemSavingsFlexibleProductService() *RedeemSavingsFlexibleProductService {
	utils.Trace("")
	return &RedeemSavingsFlexibleProductService{c: c}
}

// NewListSavingsFixedAndActivityProductsService get fixed and activity product list (Savings)
func (c *Client) NewListSavingsFixedAndActivityProductsService() *ListSavingsFixedAndActivityProductsService {
	utils.Trace("")
	return &ListSavingsFixedAndActivityProductsService{c: c}
}

// NewGetAccountSnapshotService init getting account snapshot service
func (c *Client) NewGetAccountSnapshotService() *GetAccountSnapshotService {
	utils.Trace("")
	return &GetAccountSnapshotService{c: c}
}

// NewListTradesService init listing trades service
func (c *Client) NewListTradesService() *ListTradesService {
	utils.Trace("")
	return &ListTradesService{c: c}
}

// NewHistoricalTradesService init listing trades service
func (c *Client) NewHistoricalTradesService() *HistoricalTradesService {
	utils.Trace("")
	return &HistoricalTradesService{c: c}
}

// NewListDepositsService init listing deposits service
func (c *Client) NewListDepositsService() *ListDepositsService {
	utils.Trace("")
	return &ListDepositsService{c: c}
}

// NewGetDepositAddressService init getting deposit address service
func (c *Client) NewGetDepositAddressService() *GetDepositsAddressService {
	utils.Trace("")
	return &GetDepositsAddressService{c: c}
}

// NewCreateWithdrawService init creating withdraw service
func (c *Client) NewCreateWithdrawService() *CreateWithdrawService {
	utils.Trace("")
	return &CreateWithdrawService{c: c}
}

// NewListWithdrawsService init listing withdraw service
func (c *Client) NewListWithdrawsService() *ListWithdrawsService {
	utils.Trace("")
	return &ListWithdrawsService{c: c}
}

// NewStartUserStreamService init starting user stream service
func (c *Client) NewStartUserStreamService() *StartUserStreamService {
	utils.Trace("")
	return &StartUserStreamService{c: c}
}

// NewKeepaliveUserStreamService init keep alive user stream service
func (c *Client) NewKeepaliveUserStreamService() *KeepaliveUserStreamService {
	utils.Trace("")
	return &KeepaliveUserStreamService{c: c}
}

// NewCloseUserStreamService init closing user stream service
func (c *Client) NewCloseUserStreamService() *CloseUserStreamService {
	utils.Trace("")
	return &CloseUserStreamService{c: c}
}

// NewExchangeInfoService init exchange info service
func (c *Client) NewExchangeInfoService() *ExchangeInfoService {
	utils.Trace("")
	return &ExchangeInfoService{c: c}
}

// NewGetAssetDetailService init get asset detail service
func (c *Client) NewGetAssetDetailService() *GetAssetDetailService {
	utils.Trace("")
	return &GetAssetDetailService{c: c}
}

// NewAveragePriceService init average price service
func (c *Client) NewAveragePriceService() *AveragePriceService {
	utils.Trace("")
	return &AveragePriceService{c: c}
}

// NewMarginTransferService init margin account transfer service
func (c *Client) NewMarginTransferService() *MarginTransferService {
	utils.Trace("")
	return &MarginTransferService{c: c}
}

// NewMarginLoanService init margin account loan service
func (c *Client) NewMarginLoanService() *MarginLoanService {
	utils.Trace("")
	return &MarginLoanService{c: c}
}

// NewMarginRepayService init margin account repay service
func (c *Client) NewMarginRepayService() *MarginRepayService {
	utils.Trace("")
	return &MarginRepayService{c: c}
}

// NewCreateMarginOrderService init creating margin order service
func (c *Client) NewCreateMarginOrderService() *CreateMarginOrderService {
	utils.Trace("")
	return &CreateMarginOrderService{c: c}
}

// NewCancelMarginOrderService init cancel order service
func (c *Client) NewCancelMarginOrderService() *CancelMarginOrderService {
	utils.Trace("")
	return &CancelMarginOrderService{c: c}
}

// NewCreateMarginOCOService init creating margin order service
func (c *Client) NewCreateMarginOCOService() *CreateMarginOCOService {
	utils.Trace("")
	return &CreateMarginOCOService{c: c}
}

// NewCancelMarginOCOService init cancel order service
func (c *Client) NewCancelMarginOCOService() *CancelMarginOCOService {
	utils.Trace("")
	return &CancelMarginOCOService{c: c}
}

// NewGetMarginOrderService init get order service
func (c *Client) NewGetMarginOrderService() *GetMarginOrderService {
	utils.Trace("")
	return &GetMarginOrderService{c: c}
}

// NewListMarginLoansService init list margin loan service
func (c *Client) NewListMarginLoansService() *ListMarginLoansService {
	utils.Trace("")
	return &ListMarginLoansService{c: c}
}

// NewListMarginRepaysService init list margin repay service
func (c *Client) NewListMarginRepaysService() *ListMarginRepaysService {
	utils.Trace("")
	return &ListMarginRepaysService{c: c}
}

// NewGetMarginAccountService init get margin account service
func (c *Client) NewGetMarginAccountService() *GetMarginAccountService {
	utils.Trace("")
	return &GetMarginAccountService{c: c}
}

// NewGetIsolatedMarginAccountService init get isolated margin asset service
func (c *Client) NewGetIsolatedMarginAccountService() *GetIsolatedMarginAccountService {
	utils.Trace("")
	return &GetIsolatedMarginAccountService{c: c}
}

// NewGetMarginAssetService init get margin asset service
func (c *Client) NewGetMarginAssetService() *GetMarginAssetService {
	utils.Trace("")
	return &GetMarginAssetService{c: c}
}

// NewGetMarginPairService init get margin pair service
func (c *Client) NewGetMarginPairService() *GetMarginPairService {
	utils.Trace("")
	return &GetMarginPairService{c: c}
}

// NewGetMarginAllPairsService init get margin all pairs service
func (c *Client) NewGetMarginAllPairsService() *GetMarginAllPairsService {
	utils.Trace("")
	return &GetMarginAllPairsService{c: c}
}

// NewGetMarginPriceIndexService init get margin price index service
func (c *Client) NewGetMarginPriceIndexService() *GetMarginPriceIndexService {
	utils.Trace("")
	return &GetMarginPriceIndexService{c: c}
}

// NewListMarginOpenOrdersService init list margin open orders service
func (c *Client) NewListMarginOpenOrdersService() *ListMarginOpenOrdersService {
	utils.Trace("")
	return &ListMarginOpenOrdersService{c: c}
}

// NewListMarginOrdersService init list margin all orders service
func (c *Client) NewListMarginOrdersService() *ListMarginOrdersService {
	utils.Trace("")
	return &ListMarginOrdersService{c: c}
}

// NewListMarginTradesService init list margin trades service
func (c *Client) NewListMarginTradesService() *ListMarginTradesService {
	utils.Trace("")
	return &ListMarginTradesService{c: c}
}

// NewGetMaxBorrowableService init get max borrowable service
func (c *Client) NewGetMaxBorrowableService() *GetMaxBorrowableService {
	utils.Trace("")
	return &GetMaxBorrowableService{c: c}
}

// NewGetMaxTransferableService init get max transferable service
func (c *Client) NewGetMaxTransferableService() *GetMaxTransferableService {
	utils.Trace("")
	return &GetMaxTransferableService{c: c}
}

// NewStartMarginUserStreamService init starting margin user stream service
func (c *Client) NewStartMarginUserStreamService() *StartMarginUserStreamService {
	utils.Trace("")
	return &StartMarginUserStreamService{c: c}
}

// NewKeepaliveMarginUserStreamService init keep alive margin user stream service
func (c *Client) NewKeepaliveMarginUserStreamService() *KeepaliveMarginUserStreamService {
	utils.Trace("")
	return &KeepaliveMarginUserStreamService{c: c}
}

// NewCloseMarginUserStreamService init closing margin user stream service
func (c *Client) NewCloseMarginUserStreamService() *CloseMarginUserStreamService {
	utils.Trace("")
	return &CloseMarginUserStreamService{c: c}
}

// NewStartIsolatedMarginUserStreamService init starting margin user stream service
func (c *Client) NewStartIsolatedMarginUserStreamService() *StartIsolatedMarginUserStreamService {
	utils.Trace("")
	return &StartIsolatedMarginUserStreamService{c: c}
}

// NewKeepaliveIsolatedMarginUserStreamService init keep alive margin user stream service
func (c *Client) NewKeepaliveIsolatedMarginUserStreamService() *KeepaliveIsolatedMarginUserStreamService {
	utils.Trace("")
	return &KeepaliveIsolatedMarginUserStreamService{c: c}
}

// NewCloseIsolatedMarginUserStreamService init closing margin user stream service
func (c *Client) NewCloseIsolatedMarginUserStreamService() *CloseIsolatedMarginUserStreamService {
	utils.Trace("")
	return &CloseIsolatedMarginUserStreamService{c: c}
}

// NewFuturesTransferService init futures transfer service
func (c *Client) NewFuturesTransferService() *FuturesTransferService {
	utils.Trace("")
	return &FuturesTransferService{c: c}
}

// NewListFuturesTransferService init list futures transfer service
func (c *Client) NewListFuturesTransferService() *ListFuturesTransferService {
	utils.Trace("")
	return &ListFuturesTransferService{c: c}
}

// NewListDustLogService init list dust log service
func (c *Client) NewListDustLogService() *ListDustLogService {
	utils.Trace("")
	return &ListDustLogService{c: c}
}

// NewDustTransferService init dust transfer service
func (c *Client) NewDustTransferService() *DustTransferService {
	utils.Trace("")
	return &DustTransferService{c: c}
}

// NewTransferToSubAccountService transfer to subaccount service
func (c *Client) NewTransferToSubAccountService() *TransferToSubAccountService {
	utils.Trace("")
	return &TransferToSubAccountService{c: c}
}

// NewSubaccountAssetsService init list subaccount assets
func (c *Client) NewSubaccountAssetsService() *SubaccountAssetsService {
	utils.Trace("")
	return &SubaccountAssetsService{c: c}
}

// NewSubaccountSpotSummaryService init subaccount spot summary
func (c *Client) NewSubaccountSpotSummaryService() *SubaccountSpotSummaryService {
	utils.Trace("")
	return &SubaccountSpotSummaryService{c: c}
}

// NewAssetDividendService init the asset dividend list service
func (c *Client) NewAssetDividendService() *AssetDividendService {
	utils.Trace("")
	return &AssetDividendService{c: c}
}

// NewUserUniversalTransferService
func (c *Client) NewUserUniversalTransferService() *CreateUserUniversalTransferService {
	utils.Trace("")
	return &CreateUserUniversalTransferService{c: c}
}

// NewAllCoinsInformation
func (c *Client) NewGetAllCoinsInfoService() *GetAllCoinsInfoService {
	utils.Trace("")
	return &GetAllCoinsInfoService{c: c}
}

// NewDustTransferService init Get All Margin Assets service
func (c *Client) NewGetAllMarginAssetsService() *GetAllMarginAssetsService {
	utils.Trace("")
	return &GetAllMarginAssetsService{c: c}
}

// NewFiatDepositWithdrawHistoryService init the fiat deposit/withdraw history service
func (c *Client) NewFiatDepositWithdrawHistoryService() *FiatDepositWithdrawHistoryService {
	utils.Trace("")
	return &FiatDepositWithdrawHistoryService{c: c}
}

// NewFiatPaymentsHistoryService init the fiat payments history service
func (c *Client) NewFiatPaymentsHistoryService() *FiatPaymentsHistoryService {
	utils.Trace("")
	return &FiatPaymentsHistoryService{c: c}
}

// NewPayTransactionService init the pay transaction service
func (c *Client) NewPayTradeHistoryService() *PayTradeHistoryService {
	utils.Trace("")
	return &PayTradeHistoryService{c: c}
}

// NewFiatPaymentsHistoryService init the spot rebate history service
func (c *Client) NewSpotRebateHistoryService() *SpotRebateHistoryService {
	utils.Trace("")
	return &SpotRebateHistoryService{c: c}
}

// NewConvertTradeHistoryService init the convert trade history service
func (c *Client) NewConvertTradeHistoryService() *ConvertTradeHistoryService {
	utils.Trace("")
	return &ConvertTradeHistoryService{c: c}
}

// NewGetIsolatedMarginAllPairsService init get isolated margin all pairs service
func (c *Client) NewGetIsolatedMarginAllPairsService() *GetIsolatedMarginAllPairsService {
	utils.Trace("")
	return &GetIsolatedMarginAllPairsService{c: c}
}

// NewInterestHistoryService init the interest history service
func (c *Client) NewInterestHistoryService() *InterestHistoryService {
	utils.Trace("")
	return &InterestHistoryService{c: c}
}

// NewTradeFeeService init the trade fee service
func (c *Client) NewTradeFeeService() *TradeFeeService {
	utils.Trace("")
	return &TradeFeeService{c: c}
}

// NewC2CTradeHistoryService init the c2c trade history service
func (c *Client) NewC2CTradeHistoryService() *C2CTradeHistoryService {
	utils.Trace("")
	return &C2CTradeHistoryService{c: c}
}

// NewStakingProductPositionService init the staking product position service
func (c *Client) NewStakingProductPositionService() *StakingProductPositionService {
	utils.Trace("")
	return &StakingProductPositionService{c: c}
}

// NewStakingHistoryService init the staking history service
func (c *Client) NewStakingHistoryService() *StakingHistoryService {
	utils.Trace("")
	return &StakingHistoryService{c: c}
}

// NewGetAllLiquidityPoolService init the get all swap pool service
func (c *Client) NewGetAllLiquidityPoolService() *GetAllLiquidityPoolService {
	utils.Trace("")
	return &GetAllLiquidityPoolService{c: c}
}

// NewGetLiquidityPoolDetailService init the get liquidity pool detial service
func (c *Client) NewGetLiquidityPoolDetailService() *GetLiquidityPoolDetailService {
	utils.Trace("")
	return &GetLiquidityPoolDetailService{c: c}
}

// NewAddLiquidityPreviewService init the add liquidity preview service
func (c *Client) NewAddLiquidityPreviewService() *AddLiquidityPreviewService {
	utils.Trace("")
	return &AddLiquidityPreviewService{c: c}
}

// NewGetSwapQuoteService init the add liquidity preview service
func (c *Client) NewGetSwapQuoteService() *GetSwapQuoteService {
	utils.Trace("")
	return &GetSwapQuoteService{c: c}
}

// NewSwapService init the swap service
func (c *Client) NewSwapService() *SwapService {
	utils.Trace("")
	return &SwapService{c: c}
}

// NewAddLiquidityService init the add liquidity service
func (c *Client) NewAddLiquidityService() *AddLiquidityService {
	utils.Trace("")
	return &AddLiquidityService{c: c}
}

// NewGetUserSwapRecordsService init the service for listing the swap records
func (c *Client) NewGetUserSwapRecordsService() *GetUserSwapRecordsService {
	utils.Trace("")
	return &GetUserSwapRecordsService{c: c}
}

// NewClaimRewardService init the service for liquidity pool rewarding
func (c *Client) NewClaimRewardService() *ClaimRewardService {
	utils.Trace("")
	return &ClaimRewardService{c: c}
}

// NewRemoveLiquidityService init the service to remvoe liquidity
func (c *Client) NewRemoveLiquidityService() *RemoveLiquidityService {
	utils.Trace("")
	return &RemoveLiquidityService{c: c, assets: []string{}}
}

// NewQueryClaimedRewardHistoryService init the service to query reward claiming history
func (c *Client) NewQueryClaimedRewardHistoryService() *QueryClaimedRewardHistoryService {
	utils.Trace("")
	return &QueryClaimedRewardHistoryService{c: c}
}
