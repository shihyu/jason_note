## go-okex

A Golang SDK for OKX API.

## Installation

go get github.com/tbtc-bot/go-okex

## Importing 

import (
	"github.com/tbtc-bot/go-okex"
)

## Setup 

Init client for API services. Get APIKey/SecretKey/Password from your okx account.


client := okex.NewClient("apikey", "apisecret", "password")

res, err := client.NewMaximumLoanService().InstrumentId("ETH-USDT").ManagementMode("cross").ManagementCurrency("USDT").Do(context.Background())

if err != nil {
    fmt.Println(err)
    return
}
fmt.Println(res)
