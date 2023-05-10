# 簡介
OKEX go版本的v5sdk，僅供學習交流使用。
(文檔持續完善中)
# 項目說明

## REST調用
``` go
    // 設置您的APIKey
	apikey := APIKeyInfo{
		ApiKey:     "xxxx",
		SecKey:     "xxxx",
		PassPhrase: "xxxx",
	}

	// 第三個參數代表是否為模擬環境，更多信息查看接口說明
	cli := NewRESTClient("https://www.okex.win", &apikey, true)
	rsp, err := cli.Get(context.Background(), "/api/v5/account/balance", nil)
	if err != nil {
		return
	}

	fmt.Println("Response:")
	fmt.Println("\thttp code: ", rsp.Code)
	fmt.Println("\t總耗時: ", rsp.TotalUsedTime)
	fmt.Println("\t請求耗時: ", rsp.ReqUsedTime)
	fmt.Println("\t返回消息: ", rsp.Body)
	fmt.Println("\terrCode: ", rsp.V5Response.Code)
	fmt.Println("\terrMsg: ", rsp.V5Response.Msg)
	fmt.Println("\tdata: ", rsp.V5Response.Data)
 ```
更多示例請查看rest/rest_test.go  

## websocket訂閱

### 私有頻道
```go
    ep := "wss://ws.okex.com:8443/ws/v5/private?brokerId=9999"

	// 填寫您自己的APIKey信息
	apikey := "xxxx"
	secretKey := "xxxxx"
	passphrase := "xxxxx"

	// 創建ws客戶端
	r, err := NewWsClient(ep)
	if err != nil {
		log.Println(err)
		return
	}

	// 設置連接超時
	r.SetDailTimeout(time.Second * 2)
	err = r.Start()
	if err != nil {
		log.Println(err)
		return
	}
	defer r.Stop()

	var res bool
	// 私有頻道需要登錄
	res, _, err = r.Login(apikey, secretKey, passphrase)
	if res {
		fmt.Println("登錄成功！")
	} else {
		fmt.Println("登錄失敗！", err)
		return
	}

	
	var args []map[string]string
	arg := make(map[string]string)
	arg["ccy"] = "BTC"
	args = append(args, arg)

	start := time.Now()
	// 訂閱賬戶頻道
	res, _, err = r.PrivAccout(OP_SUBSCRIBE, args)
	if res {
		usedTime := time.Since(start)
		fmt.Println("訂閱成功！耗時:", usedTime.String())
	} else {
		fmt.Println("訂閱失敗！", err)
	}

	time.Sleep(100 * time.Second)
	start = time.Now()
	// 取消訂閱賬戶頻道
	res, _, err = r.PrivAccout(OP_UNSUBSCRIBE, args)
	if res {
		usedTime := time.Since(start)
		fmt.Println("取消訂閱成功！", usedTime.String())
	} else {
		fmt.Println("取消訂閱失敗！", err)
	}
```
更多示例請查看ws/ws_priv_channel_test.go  

### 公有頻道
```go
    ep := "wss://ws.okex.com:8443/ws/v5/public?brokerId=9999"

	// 創建ws客戶端
	r, err := NewWsClient(ep)
	if err != nil {
		log.Println(err)
		return
	}

	
	// 設置連接超時
	r.SetDailTimeout(time.Second * 2)
	err = r.Start()
	if err != nil {
		log.Println(err)
		return
	}

	defer r.Stop()

	
	var args []map[string]string
	arg := make(map[string]string)
	arg["instType"] = FUTURES
	//arg["instType"] = OPTION
	args = append(args, arg)

	start := time.Now()

	// 訂閱產品頻道
	res, _, err := r.PubInstruemnts(OP_SUBSCRIBE, args)
	if res {
		usedTime := time.Since(start)
		fmt.Println("訂閱成功！", usedTime.String())
	} else {
		fmt.Println("訂閱失敗！", err)
	}

	time.Sleep(30 * time.Second)

	start = time.Now()

	// 取消訂閱產品頻道
	res, _, err = r.PubInstruemnts(OP_UNSUBSCRIBE, args)
	if res {
		usedTime := time.Since(start)
		fmt.Println("取消訂閱成功！", usedTime.String())
	} else {
		fmt.Println("取消訂閱失敗！", err)
	}
```
更多示例請查看ws/ws_pub_channel_test.go  

## websocket交易
```go
    ep := "wss://ws.okex.com:8443/ws/v5/private?brokerId=9999"

	// 填寫您自己的APIKey信息
	apikey := "xxxx"
	secretKey := "xxxxx"
	passphrase := "xxxxx"

	var res bool
	var req_id string

	// 創建ws客戶端
	r, err := NewWsClient(ep)
	if err != nil {
		log.Println(err)
		return
	}

	// 設置連接超時
	r.SetDailTimeout(time.Second * 2)
	err = r.Start()
	if err != nil {
		log.Println(err)
		return
	}

	defer r.Stop()

	res, _, err = r.Login(apikey, secretKey, passphrase)
	if res {
		fmt.Println("登錄成功！")
	} else {
		fmt.Println("登錄失敗！", err)
		return
	}

	start := time.Now()
	param := map[string]interface{}{}
	param["instId"] = "BTC-USDT"
	param["tdMode"] = "cash"
	param["side"] = "buy"
	param["ordType"] = "market"
	param["sz"] = "200"
	req_id = "00001"

	// 單個下單
	res, _, err = r.PlaceOrder(req_id, param)
	if res {
		usedTime := time.Since(start)
		fmt.Println("下單成功！", usedTime.String())
	} else {
		usedTime := time.Since(start)
		fmt.Println("下單失敗！", usedTime.String(), err)
	}

```
更多示例請查看ws/ws_jrpc_test.go  

## wesocket推送
websocket推送數據分為兩種類型數據:`普通推送數據`和`深度類型數據`。  

```go
ws/wImpl/BookData.go

// 普通推送
type MsgData struct {
	Arg  map[string]string `json:"arg"`
	Data []interface{}     `json:"data"`
}

// 深度數據
type DepthData struct {
	Arg    map[string]string `json:"arg"`
	Action string            `json:"action"`
	Data   []DepthDetail     `json:"data"`
}
```
如果需要對推送數據做處理用戶可以自定義回調函數:
1. 全局消息處理的回調函數  
該回調函數會處理所有從服務端接受到的數據。
```go
/*
	添加全局消息處理的回調函數
*/
func (a *WsClient) AddMessageHook(fn ReceivedDataCallback) error {
	a.onMessageHook = fn
	return nil
}
```
使用方法參見 ws/ws_test.go中測試用例TestAddMessageHook。

2. 訂閱消息處理回調函數  
可以處理所有非深度類型的數據，包括 訂閱/取消訂閱，普通推送數據。
```go
/*
	添加訂閱消息處理的回調函數
*/
func (a *WsClient) AddBookMsgHook(fn ReceivedMsgDataCallback) error {
	a.onBookMsgHook = fn
	return nil
}
```
使用方法參見 ws/ws_test.go中測試用例TestAddBookedDataHook。


3. 深度消息處理的回調函數  
這裡需要說明的是，Wsclient提供了深度數據管理和自動checksum的功能，用戶如果需要關閉此功能，只需要調用EnableAutoDepthMgr方法。
```go
/*
	添加深度消息處理的回調函數
*/
func (a *WsClient) AddDepthHook(fn ReceivedDepthDataCallback) error {
	a.onDepthHook = fn
	return nil
}
```
使用方法參見 ws/ws_pub_channel_test.go中測試用例TestOrderBooks。

4. 錯誤消息類型回調函數  
```go
func (a *WsClient) AddErrMsgHook(fn ReceivedDataCallback) error {
	a.OnErrorHook = fn
	return nil
}
```

# 聯繫方式
郵箱:caron_co@163.com  
微信:caron_co
