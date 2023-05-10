## 如何將OCO訂單發送到幣安



我想請你幫忙。我正在嘗試將python代碼從通過api到Binance發送限價/市價訂單更改為OCO訂單。我可以做限價單，市價單，止損限價單。我不知道該如何下OCO訂單...

當我使用限價單時，我發送的是order_type = ORDER_TYPE_LIMIT，然後我使用order = client.create_order（），它可以正常工作。當我想發送市價單時，我使用了order_type = ORDER_TYPE_MARKET，但是當我要進行OCO訂單時，我發現唯一可行的選擇是：order = client.create_oco_order（）而沒有order_type，但是在這裡我遇到了錯誤1013止損不支持此符號...

我檢查了https://api.binance.com/api/v1/exchangeInfo

並有以下“ orderTypes”：[“ LIMIT”，“ LIMIT_MAKER”，“ MARKET”，“ STOP_LOSS_LIMIT”，“ TAKE_PROFIT_LIMIT”]，“ icebergAllowed”：true，“ ocoAllowed”：true，

所以我不能使用order_type。沒有ORDER_TYPE_OCO，ocoAllowed為true，所以我應該能夠發送oco訂單。但是我收到“錯誤1013：此代碼不支持止損定單。定單失敗”。

我想要的是將“價格”設置為限價賣出訂單，以在價格到達那裡時獲得更高的獲利，並在價格下跌時將止損“ stopPrice”設置得更低... 這就是OCO的工作方式。

有人可以給我一個建議怎麼做嗎？我不是python專家，我只是在更改一個發現的代碼，我的理解是，如果允許oco，也應該允許止損。謝謝

---



為了使所有感興趣的人都能找到有關此問題的解決方案的準確答案，我將代碼包含在注釋中。

我將使用**OCO賣單**作為BTCUSDT中的示例。

假設我有1個BTC。當前價格為30157.85，我想在32000.07賣出更高的1個BTC

但是價格沒有上漲並開始下跌，因此我將止損價設置為29283.03，在該價格處以29000.00的價格開立限價賣單。

這意味著我將以32000.07或29000.00 USDT的價格賣出。該命令的編寫方式如下：

```
order= client.order_oco_sell(
    symbol= 'BTCUSDT',                                            
    quantity= 1.00000,                                            
    price= '32000.07',                                            
    stopPrice= '29283.03',                                            
    stopLimitPrice= '29000.00',                                            
    stopLimitTimeInForce= 'FOK')
```



## **生效時間訂單**

生效時間指的是您的訂單在被執行或過期之前維持有效的時間。這樣可以讓您更具體的掌握時間參數，您可以在下單時自訂時間。

幣安提供 GTC (有效直到取消)、IOC (立即成交或取消) 或 FOK (全部成交或取消) 等訂單選項：

- **GTC (有效直到取消)**：訂單將維持有效到成交或被您取消。
- **IOC (立即成交或取消)**：以可用價格及數量立即嘗試成交全部或部分訂單，然後取消剩餘未成交的訂單部分。如果您下單時所選擇的價格沒有可供應的數量，訂單將會立即被取消。請注意，此訂單類型不支持冰山委託。
- **FOK (全部成交或取消)**：訂單必須立即完全成交 (全部成交)，否則將被取消 (完全取消)。請注意，此訂單類型不支持冰山委託。



請注意，OCO訂單需要stopLimitTimeInForce參數。我使用了'FOK'值，但在這裡給您留下了可以使用的不同值的描述：[https](https://help.bybit.com/hc/en-us/articles/360039749233-What-are-time-in-force-TIF-GTC-IOC-FOK-) : [//help.bybit.com/hc/zh-CN/articles/360039749233-What-are-time-有效TIF-GTC-IOC-FOK-](https://help.bybit.com/hc/en-us/articles/360039749233-What-are-time-in-force-TIF-GTC-IOC-FOK-)

請注意，price，stopPrice，stopLimitPrice和stopLimitTimeInForce參數是字符串，而不是浮點數或十進制數。