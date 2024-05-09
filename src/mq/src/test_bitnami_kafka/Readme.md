https://qiita.com/cheuora/items/c9e7d950941cfcee4b5a

docker-compose up -d
sudo ufw allow 9092


```
@trading 
// 接口 api 
// 預警 1.3  
[
    {   
        "uuid": "1",
        "currency:" "ETH",
        "assetAmount": "50", // 
        "debtAmount": "50", // 
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "BTC",
        "assetAmount": "50",
        "debtAmount": "50", // 
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "USDT",
        "assetAmount": "50",
        "debtAmount": "50", // 
        "timestamp": 1620000000001 // msec
    },
]


// 接口 api 
// 清算買賣 eth => btc
[
    {
        "uuid": "1",
        "currency:" "ETH",
        "avgTwdPrice": "90000", // 清算價格 => okcoin/binance OTC * n%
        "avgUSDTPrice": "3000", // 清算價格 => okcoin/binance OTC (10sec) * 0.97 %
        "side": "sell",
        "amount": "20",
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "BTC",
        "avgTwdPrice": "180000", // 清算價格 => okcoin/binance OTC * n%
        "avgUSDTPrice": "60000", // 清算價格 => okcoin/binance OTC (10sec) * 1.03 n%
        "side": "buy",
        "amount": "1",
        "timestamp": 1620000000001 // msec
    },
]

// 清算買賣 usdt (3000*50+60000*10) =>  eth (50), btc (10)
[
    {
        "uuid": "1",
        "currency:" "USDT",
        "avgTwdPrice": "30", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "1", // 清算價格 => okcoin OTC * n%
        "side": "sell",
        "amount": "3000*50+60000*10",
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "ETH",
        "avgTwdPrice": "90000", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "3000", // 清算價格 => okcoin OTC * n%
        "side": "buy",
        "amount": "50",
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "BTC",
        "avgTwdPrice": "180000", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "60000", // 清算價格 => okcoin OTC * n%
        "side": "buy",
        "amount": "10",
        "timestamp": 1620000000001 // msec
    },
]
// 清算買賣 btc asset (1) => usdt debt (60000)
[
    {
        "uuid": "1",
        "currency:" "BTC",
        "avgTwdPrice": "180000", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "60000", // 清算價格 => okcoin OTC * n%
        "side": "sell",
        "amount": "1",
        "timestamp": 1620000000001 // msec
    },
    {
        "uuid": "1",
        "currency:" "USDT",
        "avgTwdPrice": "30", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "1", // 清算價格 => okcoin OTC * n%
        "side": "buy",
        "amount": "60000",
        "timestamp": 1620000000001 // msec
    }
]


// 清算買賣 twd => btc
[
    {
        "uuid": "1",
        "currency:" "BTC",
        "avgTwdPrice": "50000", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "50000", // 清算價格 => okcoin OTC * n%
        "side": "buy",
        "amount": "50",
        "timestamp": 1620000000001 // msec
    },
]
// 清算買賣 twd => usdt
[
    {
        "uuid": "1",
        "currency:" "USDT",
        "avgTwdPrice": "50000", // 清算價格 => okcoin OTC * n%
        "avgUSDTPrice": "50000", // 清算價格 => okcoin OTC * n%
        "side": "buy",
        "amount": "50",
        "timestamp": 1620000000001 // msec
    },
]
```
