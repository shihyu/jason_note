```python
import shioaji as sj
import json
from shioaji import constant


def order_cb(stat, msg):
    if "status" in msg:
        print(f"status: {json.dumps(msg['status'], indent=4)}")
        print(f"order: {json.dumps(msg['order'], indent=4)}")
        print(f"contract: {json.dumps(msg['contract'], indent=4)}")


def get_orders(api, account):
    api.update_status(account)
    trades = {t.status.id: t for t in api.list_trades()}

    for trade in trades.values():
        print(
            "Order ID: {}\nAction: {}\nStatus: {}\nStatus Value: {}\nOrder Condition: {}".format(
                trade.status.id,
                trade.order.action,
                trade.status.status,
                trade.status.status.value,
                trade.order.order_cond.value,
            )
        )
        print("-" * 30)


def cancel_all_orders(api):
    api.update_status()
    for trade in api.list_trades():
        if trade.status.status in [
            constant.Status.PreSubmitted,
            constant.Status.Submitted,
            constant.Status.PartFilled,
        ]:
            api.cancel_order(trade, timeout=0)


def test_stock(api):
    stock_contract = api.Contracts.Stocks.TSE["2890"]
    print(
        "Limit Up: {}\nLimit Down: {}".format(
            stock_contract.limit_up, stock_contract.limit_down
        )
    )

    stock_order = api.Order(
        price=23.15,
        quantity=1,
        action=constant.Action.Buy,
        price_type=constant.StockPriceType.LMT,
        order_type=constant.OrderType.ROD,
        account=api.stock_account,
    )
    stock_trade = api.place_order(stock_contract, stock_order)
    get_orders(api, api.stock_account)


def test_future(api):
    # 下單
    futures_contract = api.Contracts.Futures.TXF.TXFR1
    print(
        "Limit Up: {}\nLimit Down: {}".format(
            futures_contract.limit_up, futures_contract.limit_down
        )
    )

    futures_order = api.Order(
        action=constant.Action.Buy,
        price=21000,
        quantity=3,
        price_type=constant.FuturesPriceType.LMT,
        order_type=constant.OrderType.ROD,
        octype=constant.FuturesOCType.Auto,
        account=api.futopt_account,
    )
    futures_trade = api.place_order(futures_contract, futures_order)
    # print(f"\nFutures Trade: {futures_trade}")
    # get_orders(api, api.futopt_account)


def main():
    api = sj.Shioaji(simulation=True)
    api.login(
        api_key="",
        secret_key="",
    )

    # 設定委託回報函式
    api.set_order_callback(order_cb)

    # test_stock(api)
    test_future(api)

    # cancel_all_orders(api)
    # input("Press Enter to exit")
    api.logout()


if __name__ == "__main__":
    main()
```

